#!/usr/bin/env python

# this script will run ePo query, calculate McAfee compliance level (fresh DAT file distribution) and put everything on NAS
# 26.09.2017 Artem Ageev

import mcafee
import os
import sys
import getopt
import json
import datetime

SERVER = ''
USERNAME = ''
PASSWORD = ''
CSVFILENAME = "/logs/" + datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".csv"
REPORTFILENAME = "/data.csv"


def main():
    total_hosts = 0

    # Step 0. Open Epo connection and grab query
    epo = mcafee.client(SERVER, '8443', USERNAME, PASSWORD)
    query = epo.core.executeQuery('439')  # get query  "DAT file distribution". epo.core.listQueries will show all

    # Step 1. Get query and output to CSV
    csvfile = open(CSVFILENAME, "w")
    for q in query:
        #   print(q[u'EPOProdPropsView_VIRUSCAN.datver'], q[u'count'])
        csvfile.write(json.dumps(q[u'EPOProdPropsView_VIRUSCAN.datver']) + ";" + json.dumps(q[u'count']) + "\n")
    csvfile.close()

    # Step 2. Process logs. Build final report
    for q in query:
        total_hosts += int(json.dumps(q[u'count']))

    last_6_days_DAT_hosts = int(json.dumps(query[0][u'count']))+int(json.dumps(query[1][u'count']))+ \
                                                    int(json.dumps(query[2][u'count']))+int(json.dumps(query[3][u'count']))+ \
                                                    int(json.dumps(query[4][u'count']))+int(json.dumps(query[5][u'count']))

    current_compliance_level = (last_6_days_DAT_hosts * 100 / total_hosts) #int is always bigger then 1
    DAT_0_share = int(json.dumps(query[0][u'count'])) * 100 / total_hosts
    DAT_1_share = int(json.dumps(query[1][u'count'])) * 100 / total_hosts
    DAT_2_share = int(json.dumps(query[2][u'count'])) * 100 / total_hosts
    DAT_3_share = int(json.dumps(query[3][u'count'])) * 100 / total_hosts
    DAT_4_share = int(json.dumps(query[4][u'count'])) * 100 / total_hosts
    DAT_5_share = int(json.dumps(query[5][u'count'])) * 100 / total_hosts
    old_DAT_share = 100 - current_compliance_level

    reportfile = open(REPORTFILENAME, "a")
    reportfile.write(datetime.datetime.now().strftime("%Y-%m-%d") + ";" + str(current_compliance_level) + ";" + \
                     str(total_hosts) + ";" + str(last_6_days_DAT_hosts) + ";" + str(DAT_0_share) + ";" + \
                     str(DAT_1_share) + ";" + str(DAT_2_share) + ";" + str(DAT_3_share) + ";" + str(DAT_4_share) + ";" + \
                     str(DAT_5_share) + ";" + str(old_DAT_share) + "\n" )
    reportfile.close()

main()
