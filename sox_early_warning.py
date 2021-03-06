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

PATCH_DATA_FILE = '/data.csv'

DAYS_INCOMPLIANT_THRESHOLD = 10

COUNTRY_LIST = ['']

ADDRESS_BOOK = {''}

def main():
    # step 0. initialize / define everything
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # step 1. get patch data
    with open(PATCH_DATA_FILE) as f:
        reader = csv.reader(f, delimiter=';')
        patch_data = [row for row in reader]

    if patch_data[-1][0] == today: #run only if todays data available
        for i in range(1, len(patch_data[-1]), 2):
            #find incompliant countries
            if float(patch_data[-1][i+1].replace(",",".")) < 90:
                recepients = []
                country = COUNTRY_LIST[int((i+1)/2)-1]
                recepients.append(ADDRESS_BOOK[country])
                # check history for 14 days and maybe mark as incompliant
                j = 1
                while float(patch_data[-j][i+1].replace(",",".")) < 90:
                    j += 1

                 # step 4. form MSG and send daily report
                if recepients and (j - 1) > DAYS_INCOMPLIANT_THRESHOLD:
                    send_mail(recepients, country, (j - 1))

def send_mail(recepients, country, days_incompliant):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = '[Patching] Low patch status in ' + country + ' for ' + str(days_incompliant) + ' days'
    msg['From'] = MAIL_SENDER
    msg['To'] = ", ".join(recepients)
    msg['CC'] = MAIL_CC

    # Create the body of the message (a plain-text and an HTML version).
    text = "NSO's patch status is low for %s days in a row. More details in SCCM report" % (days_incompliant)
    html = """\
    <html>
      <head></head>
      <body>
        <p>
            *this mail was automatically generated*<br>
            <br>
            Hi!<br>
            More than 10%% of active workstations in your NSO have troubles fetching Windows updates. Please have a look at the 
            <a href='http://'>
            SCCM report</a> (numbers are clickable).<br>
            <br>
            If NSO is incompliant for more than 14 days - incident tickets will be raised via ITRP.<br>
            &nbsp;&nbsp;&nbsp;&nbsp;Days incompliant: %s<br>
            <br>
            <br>
            Regards,<br>
            SecOpsBot<br>            
        </p>
      </body>
    </html>
    """ % (days_incompliant)

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    recepients.append(MAIL_CC)

    s = smtplib.SMTP(SMTP_SERVER)
    s.sendmail(MAIL_SENDER, recepients, msg.as_string())
    s.quit()

    print('[INFO] Mail to ' + ", ".join(recepients) + ' -' + country + '- successfully sent')

main()
