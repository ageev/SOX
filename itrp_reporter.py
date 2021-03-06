#!/usr/bin/env python

import os
import sys
import getopt
import json
import requests
import csv
import time
import datetime

#from requests.packages.urllib3.exceptions import InsecureRequestWarning
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_TOKEN = ''
ITRP_URL = 'https://api.itrp.com/v1/'
HEADERS = {'X-ITRP-Account' : '', 'Content-Type' : 'application/json'}
CONNECTION_DELAY = 1

REPORTFILENAME = "//data.csv"

#pretty print
#print(json.dumps(r.json()[0], indent=4, sort_keys=True))


def main():
	
	assigned = 0
	accepted = 0
	in_progress = 0
	waiting_for_customer = 0
	waiting_for = 0
	total = 0

	r = requests.get(ITRP_URL+"requests"+"?api_token="+API_TOKEN + "&team=5807&status=assigned&per_page=100" , headers = HEADERS)

	for i in r.json():
	#	print(i["id"])
		assigned += 1

	r = requests.get(ITRP_URL+"requests"+"?api_token="+API_TOKEN + "&team=5807&status=accepted&per_page=100" , headers = HEADERS)

	for i in r.json():
		accepted += 1

	r = requests.get(ITRP_URL+"requests"+"?api_token="+API_TOKEN + "&team=5807&status=in_progress&per_page=100" , headers = HEADERS)

	for i in r.json():
		in_progress += 1

	r = requests.get(ITRP_URL+"requests"+"?api_token="+API_TOKEN + "&team=5807&status=waiting_for&per_page=100" , headers = HEADERS)

	for i in r.json():
		waiting_for += 1

	r = requests.get(ITRP_URL+"requests"+"?api_token="+API_TOKEN + "&team=5807&status=waiting_for_customer&per_page=100" , headers = HEADERS)

	for i in r.json():
		waiting_for_customer += 1

	total = assigned + accepted + in_progress + waiting_for_customer + waiting_for

	write_report([total, assigned, accepted, in_progress, waiting_for, waiting_for_customer])

def write_report(data):
	data.insert(0, str(datetime.datetime.now().strftime("%Y-%m-%d")))
	with open(REPORTFILENAME, 'a') as myfile:
		wr = csv.writer(myfile, delimiter =';')
		wr.writerow(data)

main()
