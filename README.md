# SOX
SOX reporting automation.
# Environment
## OS
tested on Ubuntu 17.04, 17.10
## Log source
mount NAS via /etc/fstab file:
//nas/security_operations$   /media/nas01    cifs     vers=1.0,username=,domain=,password=,iocharset=utf8,sec=ntlm,file_mode=0777,dir_mode=0777 0       0
## Schedule reports
crontab -e
00 7 * * 1-5 /var/opt/sox/sox_mailer >/dev/null 2>&1
45 6 * * * /var/opt/sox/sccm_sox_reporter >/dev/null 2>&1
50 6 * * * /var/opt/sox/mcafee_sox_reporter >/dev/null 2>&1
55 6 * * 1-5 PYTHONPATH=/usr/lib/python2.7/dist-packages /var/opt/sox/itrp_reporter >/dev/null 2>&1
05 7 * * 1-5 /var/opt/sox/sox_early_warning >/dev/null 2>&1
