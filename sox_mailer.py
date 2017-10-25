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
MAIL_RECEPIENT = ''

AV_DATA_FILE = '/media/nas01/Controls/McAfee daily reports/data.csv'
PATCH_DATA_FILE = '/media/nas01/Controls/SCCM daily reports/data.csv'

#AV_DATA_FILE = 'r:/Controls/McAfee daily reports/data.csv'
#PATCH_DATA_FILE = 'r:/Controls/SCCM daily reports/data.csv'

COUNTRY_LIST = ['CAT', 'CBL', 'CCH', 'CCZ', 'CDE', 'CDK', 'CEA', 'CEE', 'CEL', 'CES', 'CEU', \
				'CFI', 'CFR', 'CHU', 'CIT', 'CME', 'CNL', 'CNO', 'CPL', 'CPT', 'CRU', 'CSE', \
				'CSK', 'CUK', 'CZA', 'IBE', 'IDE']

def main():
	# step 0. initialize / define everything
	dat_compliance_level = 'Error!'   #default value
	patch_compliance_level = 'Error!'
	countries_below_90 = ''

	total = 0
	unpatched_pc = 0

	# step 1. grab McAfee DAT file data
	with open(AV_DATA_FILE) as f:
		reader = csv.reader(f, delimiter=';')
		av_data = [row for row in reader]
	if av_data[-1][0] != datetime.datetime.now().strftime("%Y-%m-%d"):
		dat_compliance_level = "no today's data available"
	else:
		dat_compliance_level = str(av_data[-1][1]) + "%"

	# step 2. get patch data
	with open(PATCH_DATA_FILE) as f:
		reader = csv.reader(f, delimiter=';')
		patch_data = [row for row in reader]
	if patch_data[-1][0] != datetime.datetime.now().strftime("%Y-%m-%d"):
		patch_compliance_level = "no today's data available"
	else:
		#calculate total number of PCs in last entry and number of unpatched PC
		for i in range(1, len(patch_data[-1]), 2):
			total += int(patch_data[-1][i])
			unpatched_pc += round(int(patch_data[-1][i]) * (1 - float(patch_data[-1][i+1].replace(",",".")) / 100))
			if float(patch_data[-1][i+1].replace(",",".")) < 90:
				countries_below_90 += COUNTRY_LIST[int((i+1)/2)-1] + ', '
		if not countries_below_90:
			countries_below_90 = 'none'
		patch_compliance_level = str(round(100*(1- unpatched_pc/total),2)) + "%"

	# step 3. from MSG and send daily report
	send_sox_mail(dat_compliance_level, patch_compliance_level, countries_below_90)

def send_sox_mail(dat_compliance_level, patch_compliance_level, countries_below_90):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = '[SOX Daily] AV - ' + dat_compliance_level + ', Patch - ' + patch_compliance_level
	msg['From'] = MAIL_SENDER
	msg['To'] = MAIL_RECEPIENT

	# Create the body of the message (a plain-text and an HTML version).
	text = "AV DAT level: %s\nPatch level: %s\nCountries with patch level below 90 percent: %s\n" % (dat_compliance_level, patch_compliance_level, countries_below_90)
	html = """\
	<html>
	  <head></head>
	  <body>
	    <p>AV DAT level: <a href="r:\Controls\McAfee daily reports\McAfee SOX DAT file distribution v1.xlsx">%s</a><br>
	       Patch level: <a href="r:\Controls\SCCM daily reports\Canon Patch Distribution v1.xlsx">%s</a><br>
	       Countries with patch level below 90 percent: %s<br>
	       <br>
	       <a href='http://server/ReportServer_S1/Pages/ReportViewer.aspx?%%2FCanon%%20Reports%%20(Desktops)%%2FCanon%%20Health%%20Check%%20Reports%%2FCanon%%20Health%%20Check%%20Report%%20v2'>SCCM report</a><br>
	    </p>
	  </body>
	</html>
	""" % (dat_compliance_level, patch_compliance_level, countries_below_90)

	part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)

	s = smtplib.SMTP(SMTP_SERVER)
	s.sendmail(MAIL_SENDER, MAIL_RECEPIENT, msg.as_string())
	s.quit()

main()
