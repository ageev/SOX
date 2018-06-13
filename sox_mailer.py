#!/usr/bin/env python3

# this script will send daily report
# Important! to run on unix:
# 1. remove extension
# 2. run dos2unix <file> to fix newline issue
# 3. chmod +x <file>
# 4. copy to /etc/cron.daily
# =============================
# v1 27.09.2017 (c) Artem Ageev

import smtplib
import textwrap
import os
import sys
import csv
import time
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = ''
MAIL_SENDER = ''
MAIL_CC = ''
MAIL_RECEPIENTS = ['']

if os.path.exists('/Controls/'):
	AV_DATA_FILE = '/data.csv'
	PATCH_DATA_FILE = '/data.csv'
	ITRP_DATA_FILE = '/data.csv'
else:
	AV_DATA_FILE = '/data.csv'
	PATCH_DATA_FILE = '/data.csv'
	ITRP_DATA_FILE = "/data.csv"

COUNTRY_LIST = ['']

def main():
	# step 0. initialize / define everything
	dat_compliance_level = 'Error!'   #default value
	patch_compliance_level = 'Error!'
	countries_below_90 = ''
	countries_patch_incompliant = ''
	itrp_total = 'Error!'
	itrp_total_diff = 'Error!'
	today = datetime.datetime.now().strftime("%Y-%m-%d")

	total = 0
	unpatched_pc = 0

	# step 1. grab McAfee DAT file data
	with open(AV_DATA_FILE) as f:
		reader = csv.reader(f, delimiter=';')
		av_data = [row for row in reader]
	if av_data[-1][0] != today:
		dat_compliance_level = "no today's data available"
	else:
		dat_compliance_level = str(av_data[-1][1]) + "%"
		if (av_data[-1][4] == '0') and (av_data[-1][5] == '0'):
			dat_compliance_level += " [!] No fresh DAT for 2d+"

	# step 2. get patch data
	with open(PATCH_DATA_FILE) as f:
		reader = csv.reader(f, delimiter=';')
		patch_data = [row for row in reader]
	if patch_data[-1][0] != today:
		patch_compliance_level = "no today's data available"
	else:
		#calculate total number of PCs in last entry and number of unpatched PC
		for i in range(1, len(patch_data[-1]), 2):
			total += int(patch_data[-1][i])
			unpatched_pc += round(int(patch_data[-1][i]) * (1 - float(patch_data[-1][i+1].replace(",",".")) / 100))
			if float(patch_data[-1][i+1].replace(",",".")) < 90:
				countries_below_90 += COUNTRY_LIST[int((i+1)/2)-1] + ', '
				# check history for 14 days and maybe mark as incompliant
				flag = False
				for j in range(1, 16):
					try:
						if float(patch_data[-j][i+1].replace(",",".")) > 90:
							flag = True
					except:
						flag = True #exit if there is not enough data (less the 14 days data available)
				if flag == False:
					countries_patch_incompliant += COUNTRY_LIST[int((i+1)/2)-1] + ', '

		patch_compliance_level = str(round(100*(1- unpatched_pc/total),2)) + "%"
	
	if not countries_below_90:
		countries_below_90 = 'none'
	if not countries_patch_incompliant:
		countries_patch_incompliant = 'none'

	# step 3
	with open(ITRP_DATA_FILE) as f:
		reader = csv.reader(f, delimiter=';') #another delimiter!
		itrp_data = [row for row in reader]
	if itrp_data[-1][0] != today:
		itrp_total = "no today's data available"
	else:
		itrp_total = str(itrp_data[-1][1])
		diff = int(itrp_data[-1][1]) - int(itrp_data[-2][1])
		if diff <= 0:
			itrp_total_diff = str(diff)
		else:
			itrp_total_diff = "+" + str(diff)

	# step 4. form MSG and send daily report
	send_sox_mail(dat_compliance_level, patch_compliance_level, countries_below_90, countries_patch_incompliant, itrp_total, itrp_total_diff)

def send_sox_mail(dat_compliance_level, patch_compliance_level, countries_below_90, countries_patch_incompliant, itrp_total, itrp_total_diff):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = '[SOX Daily] AV - ' + dat_compliance_level + ', Patch - ' + patch_compliance_level + ', ITRP - ' + itrp_total
	msg['From'] = MAIL_SENDER
	msg['To'] = ", ".join(MAIL_RECEPIENTS)
	msg['CC'] = MAIL_CC

	# Create the body of the message (a plain-text and an HTML version).
	text = "AV DAT level: {0}\nPatch level: {1}\nCountries with patch level below 90 percent: {2}\nITRP queue: {3}\n".format(dat_compliance_level, 
		patch_compliance_level, countries_below_90, itrp_total)
	html = """\
	<html>
	  <head></head>
	  <body>
	    <p>AV DAT level: <a href="McAfee SOX DAT file distribution v1.xlsx">{0}</a><br>
	       Patch level: <a href="Patch Distribution v1.xlsx">{1}</a><br>
	       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Countries with patch level below 90 percent: {2}<br>
	       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Countries incompliant for more than 14 days: {3}<br>
	       ITRP queue: <a href="">{4}</a> ({5} since yesterday)<br>
	       <br>
	       <a href=''>SCCM report</a><br>
	    </p>
	  </body>
	</html>
	""".format(dat_compliance_level, patch_compliance_level, countries_below_90, countries_patch_incompliant, itrp_total, itrp_total_diff)

	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)
	
	MAIL_RECEPIENTS.append(MAIL_CC)
	s = smtplib.SMTP(SMTP_SERVER)
	s.sendmail(MAIL_SENDER, MAIL_RECEPIENTS, msg.as_string())
	s.quit()

main()
