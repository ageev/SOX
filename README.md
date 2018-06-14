# SOX
SOX reporting automation. Those scripts are highly specialised for my current employer. Yes, sometimes I use Github for backup :)
Don't worry, all code is sanitized. 

# Environment
## OS
tested on Ubuntu 17.04, 17.10
## Log source
mount NAS via /etc/fstab file. SMBv1 should be used due to known issues with Samba and SMBv2:
//nas/folder$   /media/nas01    cifs     vers=1.0,username=,domain=,password=,iocharset=utf8,sec=ntlm,file_mode=0777,dir_mode=0777 0       0
## Schedule reports
crontab -e

use custom module path
55 6 * * 1-5 PYTHONPATH=/usr/lib/python2.7/dist-packages /itrp_reporter >/dev/null 2>&1

normal record
05 7 * * 1-5 /sox_early_warning >/dev/null 2>&1
