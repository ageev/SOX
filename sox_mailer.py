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

SMTP_SERVER = 'smtp'
MAIL_SENDER = 'artem.ageev@domain.com'
MAIL_CC = 'cc@domain.com'
MAIL_RECEPIENTS = ['Employees@domain.com']

if os.path.exists('C:/Windows'):
        AV_DATA_FILE = 'r:/Controls/McAfee daily reports/data.csv'
        AV_DATA_FILE_ENS = 'r:/Controls/McAfee daily reports/data_ens.csv'
        AV_DATA_FILE_NEW_VSE = 'r:/Controls/McAfee daily reports/data_new_VSE.csv'
        PATCH_DATA_FILE = 'r:/Controls/SCCM daily reports/data.csv'
        ITRP_DATA_FILE = 'r:/Controls/ITRP daily reports/data.csv'
        BITLOCKER_FILE = 'r:/Controls/SCCM daily reports/Bitlocker.csv'
else:
        AV_DATA_FILE = '/media/nas01/Controls/McAfee daily reports/data.csv'
        AV_DATA_FILE_ENS = '/media/nas01/Controls/McAfee daily reports/data_ens.csv'
        AV_DATA_FILE_NEW_VSE = '/media/nas01/Controls/McAfee daily reports/data_new_VSE.csv'
        PATCH_DATA_FILE = '/media/nas01/Controls/SCCM daily reports/data.csv'
        ITRP_DATA_FILE = '/media/nas01/Controls/ITRP daily reports/data.csv'
        BITLOCKER_FILE = '/media/nas01/Controls/SCCM daily reports/Bitlocker.csv'

COUNTRY_LIST = ['RUS', 'UK']

def main():
        # step 0. initialize / define everything
        dat_compliance_level = 'Error!'   #default value
        dat_compliance_level_total = 'Error!'
        dat_compliance_level_ens = 'Error!'
        dat_compliance_level_ens_total = 'Error!'
        dat_compliance_level_new_vse = 'Error!'
        dat_compliance_level_new_vse_total = 'Error!'
        patch_compliance_level = 'Error!'
        countries_below_90 = ''
        countries_patch_incompliant = ''
        itrp_total = 'Error!'
        itrp_total_diff = 'Error!'
        Bitlocker_level = 'Error!'
        No_BitLocker_countries_below_98 = ''
        No_BitLocker_countries_incompliant = ''

        today = datetime.datetime.now().strftime("%Y-%m-%d")

        total = 0
        unpatched_pc = 0

        total_bitLocker = 0
        NO_bitlocker_pc = 0


        # step 1. grab McAfee DAT file data
        with open(AV_DATA_FILE) as f:
                reader = csv.reader(f, delimiter=';')
                av_data = [row for row in reader]
        if av_data[-1][0] != today:
                dat_compliance_level = "no today's data available"
        else:
                dat_compliance_level = str(av_data[-1][1]) + "%"
                dat_compliance_level_total = str(av_data[-1][2])
                if (av_data[-1][4] == '0') and (av_data[-1][5] == '0'):
                        dat_compliance_level += " [!] No fresh DAT for 2d+"

        # step 1a. grab McAfee DAT file data from ENS server
        with open(AV_DATA_FILE_ENS) as f:
                reader = csv.reader(f, delimiter=';')
                av_data = [row for row in reader]
        if av_data[-1][0] != today:
                dat_compliance_level_ens = "no today's data available"
        else:
                dat_compliance_level_ens = str(av_data[-1][1]) + "%"
                dat_compliance_level_ens_total = str(av_data[-1][2])

        # step 1b. grab McAfee DAT file data from NEW VSE server
        with open(AV_DATA_FILE_NEW_VSE) as f:
                reader = csv.reader(f, delimiter=';')
                av_data = [row for row in reader]
        if av_data[-1][0] != today:
                dat_compliance_level_new_vse = "no today's data available"
        else:
                dat_compliance_level_new_vse = str(av_data[-1][1]) + "%"
                dat_compliance_level_new_vse_total = str(av_data[-1][2])

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


        #step 4. get Bitlocker data

        with open(BITLOCKER_FILE) as f:
                reader = csv.reader(f, delimiter=';')
                bitlocker_data = [row for row in reader]
        if bitlocker_data[-1][0] != today:
                Bitlocker_level = "no today's data available"
        else:
                #calculate total number of PCs in last entry and number of incomplaint PC
                for i in range(1, len(bitlocker_data[-1]), 2):
                        total_bitLocker += int(bitlocker_data[-1][i])
                        
                        NO_bitlocker_pc += round(int(bitlocker_data[-1][i]) * (1 - float(bitlocker_data[-1][i+1].replace(",",".")) / 100))
                        if float(bitlocker_data[-1][i+1].replace(",",".")) < 98:
                                No_BitLocker_countries_below_98 += COUNTRY_LIST[int((i+1)/2)-1] + ', '
                                # check history for 14 days and maybe mark as incompliant
                                flag = False
                                for j in range(1, 16):
                                        try:
                                                if float(bitlocker_data[-j][i+1].replace(",",".")) > 98:
                                                        flag = True
                                        except:
                                                flag = True #exit if there is not enough data (less the 14 days data available)
                                if flag == False:
                                        No_BitLocker_countries_incompliant += COUNTRY_LIST[int((i+1)/2)-1] + ', '

                Bitlocker_level = str(round(100*(1- NO_bitlocker_pc/total_bitLocker),2)) + "%"
                

        if not No_BitLocker_countries_below_98:
                No_BitLocker_countries_below_98 = 'none'
        if not No_BitLocker_countries_incompliant:
                No_BitLocker_countries_incompliant = 'none'

        # step 5. form MSG and send daily report
        send_sox_mail(dat_compliance_level,
                dat_compliance_level_total,
                dat_compliance_level_ens,
                dat_compliance_level_ens_total,
                dat_compliance_level_new_vse,
                dat_compliance_level_new_vse_total,
                patch_compliance_level,
                countries_below_90,
                countries_patch_incompliant,
                itrp_total,
                itrp_total_diff,
                Bitlocker_level,
                No_BitLocker_countries_below_98,
                No_BitLocker_countries_incompliant
                )



def send_sox_mail(dat_compliance_level,
                dat_compliance_level_total,
                dat_compliance_level_ens,
                dat_compliance_level_ens_total,
                dat_compliance_level_new_vse,
                dat_compliance_level_new_vse_total,
                patch_compliance_level,
                countries_below_90,
                countries_patch_incompliant,
                itrp_total,
                itrp_total_diff,
                Bitlocker_level,
                No_BitLocker_countries_below_98,
                No_BitLocker_countries_incompliant
                ):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[SOX Daily] AV - ' + dat_compliance_level \
                        + ', ENS - ' + dat_compliance_level_ens \
                        + ', NEW VSE - ' + dat_compliance_level_new_vse \
                        + ',Patch - ' + patch_compliance_level \
                        + ', ITRP - ' + itrp_total \
                        + ' , Bitlocker - ' + Bitlocker_level
        msg['From'] = MAIL_SENDER
        msg['To'] = ", ".join(MAIL_RECEPIENTS)
        msg['CC'] = MAIL_CC

        # Create the body of the message (a plain-text and an HTML version).
        text = "please see HTML part of the message"
        html = """\
        <html>
          <head></head>
          <body>
            <p>AV DAT level: <a href="r:\\Controls\\McAfee daily reports\\McAfee SOX DAT file distribution v1.xlsx">{0}</a>. Total {1} systems<br>
            ENS DAT level: <a href="r:\\Controls\\McAfee daily reports\\ENS SOX.xlsx">{2}</a>. Total {3} systems<br>
            NEW VSE DAT level: <a href="r:\\Controls\\McAfee daily reports\\NEW VSE SOX.xlsx">{4}</a>. Total {5} systems<br>
               Patch level: <a href="r:\\Controls\\SCCM daily reports\\Patch Distribution v1.xlsx">{6}</a><br>
               &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Countries with patch level below 90 percent: {7}<br>
               &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Countries incompliant for more than 14 days: {8}<br>
               ITRP queue: <a href="https://canonit.itrp.com/inbox?vstate=assigned_to_my_team">{9}</a> ({10} since yesterday)<br>
               <br>

               BitLocker level: <a href="r:\\Controls\\SCCM daily reports\\BitLocker Distribution v1.xlsx">{11}</a><br>
               &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Countries with BitLocker level below 98 percent: {12}<br>
               &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; BitLockerCountries incompliant for more than 14 days: {13}<br><br>

               <a href='http://srv/Reports_S1/Pages/Report.aspx?ItemPath=%2fWorkstations+Compliancy%2fWorkstations+Compliancy+Report'>SCCM report</a><br>
            </p>
          </body>
        </html>
        """.format(dat_compliance_level,
                dat_compliance_level_total,
                dat_compliance_level_ens,
                dat_compliance_level_ens_total,
                dat_compliance_level_new_vse,
                dat_compliance_level_new_vse_total,
                patch_compliance_level,
                countries_below_90,
                countries_patch_incompliant,
                itrp_total,
                itrp_total_diff,
                Bitlocker_level,
                No_BitLocker_countries_below_98,
                No_BitLocker_countries_incompliant
                )

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