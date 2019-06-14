#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  run.py
#
#  Copyleft 2018 VIAA vzw
#  <admin@viaa.be>
#
#  @author: https://github.com/maartends
#
#######################################################################
#
#  batch-reporter
#
#  See README.md
#
#  export HTTP_PROXY='http://proxy:80'
#  export HTTPS_PROXY='https://proxy:80'
#
#######################################################################

# Standard imports
import sys
import logging
import argparse
import csv
import re
import urllib.parse
# 3d party imports
import yaml
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Create logger
LOG_FMT = '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s'
log = logging.getLogger('batch-reporter')
log.setLevel(logging.DEBUG)

# create handler and set level to debug
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(LOG_FMT)
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
log.addHandler(ch)
# + file
file_log = logging.FileHandler(filename='./batch-reporter.log')
file_log.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(LOG_FMT)
# add formatter to file_log
file_log.setFormatter(formatter)
# add file_log to logger
log.addHandler(file_log)


# DEFINE SOME CONSTS
DEFAULT_CFG_FILE = './config.yml'
with open(DEFAULT_CFG_FILE, 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
# PRD Public base url
MH_BASE_URL = cfg['environment']['host']

TIMEOUT         = cfg['request']['timeout']
REQ_HEADERS     = cfg['request']['headers']
REQ_SESSION     = requests.Session()
REQ_SESSION.headers.update(REQ_HEADERS)
REQ_SESSION.auth = (cfg['credentials']['user'],
                    cfg['credentials']['passwd'])
SESS_RETRIES    = Retry(total=5, backoff_factor=1,
                        status_forcelist=[502, 503, 504])
REQ_SESSION.mount('http://', HTTPAdapter(max_retries=SESS_RETRIES))

CSV_HEADER = ('headers', 'filename', 'tape_label', 'ingest_date')


def get_batch_records_mtd(mtd_file):
    """Returns a list"""
    with open(mtd_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    return [x for x in reader]


def get_batch_records_mh(batch):
    """Returns a list of dict objects"""
    query_params = {"q": "+(dc_identifier_localidsbatch:%s)" % batch,
                    "nrOfResults": 10000}
    response = REQ_SESSION.get(MH_BASE_URL, params=query_params)
    j = response.json()
    return j


def compare_records(mtd_records, mh_records):
    """Compare two list of dicts and return a list of dicts"""
    # Init the result-list
    result = []
    # We start with the mtd-record list
    for mtd_rec in mtd_records:
        filename = mtd_rec['filename']
        mh_rec = get_mh_record(mh_records, filename=filename)
        if mh_rec:
            status = mh_rec.get('Internal').get('ArchiveStatus')
        else:
            status = 'NOTFOUND'
        result.append({
            'filename': filename,
            'status': status,
        })
    return result


def get_mh_record(mh_records, filename=None, md5=None):
    res = list(filter(lambda rec:
                      rec['Descriptive']['Title'] == filename, mh_records))
    if res:
        return res[0]
    return None


def get_resource(media_id):
    url = urllib.parse.urljoin(MH_BASE_URL, media_id)
    response = REQ_SESSION.get(url)
    return response.json()


def format_archivedate(archivedate: str) -> str:
    # `archivedate` comes in EXIF format, so, for example:
    # "2019:03:22 12:32:11", which we split at a word-boundary to get the
    # substituent parts (proper date parsing would be better, agreed)
    parts = re.findall(r"[\w']+", archivedate)
    return '%s%s%s' % (parts[0], parts[1], parts[2])


def write_compare_list(compare_list, batchname):
    """"""
    output_filename = '%s.csv' % batchname
    log.info('Writing to "%s"' % output_filename)
    fieldnames = ['filename', 'status']
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(compare_list)


def write_stdout_report(records):
    """Output summary of records statusses to stdout."""
    # statusses = ['on_tape', 'in_progress', 'failed']
    on_tape = len([
        x for x in records['MediaDataList'] if
        x['Internal']['ArchiveStatus'] == 'on_tape'])
    in_progress = len([
        x for x in records['MediaDataList'] if
        x['Internal']['ArchiveStatus'] == 'in_progress'])
    failed = len([
        x for x in records['MediaDataList'] if
        x['Internal']['ArchiveStatus'] == 'failed'])
    print('***************************')
    print('*  on_tape     = %s *' % on_tape)
    print('*  in_progress = %s *' % in_progress)
    print('*  failed      = %s *' % failed)
    print('*  ------------------')
    print('*  total       = %s *' % sum([on_tape, in_progress, failed]))
    print('***************************')


def write_report(records, batchname, status):
    output_filename_fmt = '{nr_of_recs}-{status}-at_viaa-{batchname}.csv'
    output_filename = output_filename_fmt.format(
        nr_of_recs = len(records),
        status     = status,
        batchname  = batchname,
    )
    # Make lines
    lines = []
    for record in records:
        filename = record['Descriptive']['Title']
        archivedate = format_archivedate(
            record['Administrative']['ArchiveDate']
        )
        lines.append((
            filename, 'FTP', archivedate
        ))
    log.info('Writing to "%s"' % output_filename)
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(CSV_HEADER)
        writer.writerows(lines)


def main(cmd_args):
    log.info('Start querying batch "%s"' % cmd_args.batch)
    if cmd_args.mtd:
        log.info('Getting batch records from mtd-file: "%s"' % cmd_args.mtd)
        mtd_records = get_batch_records_mtd(cmd_args.mtd)
        log.info('# of records in mtd-file: %s' % len(mtd_records))
    # Get batch records from MediaHaven
    log.info('Getting batch records from MH "%s"' % cmd_args.batch)
    mh_records = get_batch_records_mh(cmd_args.batch)
    log.info(
        '# of records in batch (MediaHaven): %s' %
        mh_records['TotalNrOfResults'])
    if cmd_args.mtd:
        compare_list = compare_records(
            mtd_records,
            mh_records['MediaDataList']
        )
        write_compare_list(compare_list, cmd_args.batch)
    ok_status = cfg['ok_status']
    # Get oks
    ok_list = [
        x for x in mh_records['MediaDataList'] if
        x['Internal']['ArchiveStatus'] == ok_status]
    log.debug('ok_list: %s' % len(ok_list))
    write_report(ok_list, cmd_args.batch, 'ok')
    # Get noks
    nok_list = [
        x for x in mh_records['MediaDataList'] if
        x['Internal']['ArchiveStatus'] != ok_status]
    log.debug('nok_list: %s' % len(nok_list))
    write_report(nok_list, cmd_args.batch, 'nok')
    write_stdout_report(mh_records)


if __name__ == '__main__':
    # Parse the command line
    parser = argparse.ArgumentParser(prog="batch-reporter",
                                     description="""Report on batches""")
    parser.add_argument(dest='batch', type=str, help='''Specify batchname.''')
    parser.add_argument('-m', '--mtd', dest='mtd',
                        required=False, help='''Filepath to mtd (csv) file.''')
    cmd_args = parser.parse_args()
    main(cmd_args)


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 smartindent
