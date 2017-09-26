#!/usr/bin/env python

# This file will grab required data from SCCM reports and create Data.csv file for SOX reporting

import os
import sys
import csv
import time


LOG_DIR = '/media/'
DATA_DIR = '/media/'

def main():

	rename_files(LOG_DIR)
	build_data_file(DATA_DIR, LOG_DIR)


def build_data_file(dir, logs): #will build (or append if exists) data.csv file based on logs from "Logs" dir
	#clear Data.csv file
	open(dir + 'data.csv', 'w').close()

	for subdir, dirs, files in os.walk(logs):
		for file in files:
			patch_data =''
			data = ''

			#read data
			filename = os.path.join(subdir, file)
			with open(filename) as f:
				data = list(csv.DictReader(f.readlines()[28:55], delimiter=',', dialect='excel')) 

			#build data
			patch_data = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(filename))) + ";"
			for i in data:
				patch_data += i['Count'] + ";" + i['Patch__'] + ';'
			patch_data += "\n"

			#replace "." with "," for correct EXCEL handling
			patch_data = patch_data.replace(".", ",")

			#write data
			with open(dir + 'data.csv', "a") as f:
				f.write(patch_data)

def rename_files(dir): #will rename all files in DIR according to Last Modified file time property
	for subdir, dirs, files in os.walk(dir):
		for file in files:
			filename = os.path.join(subdir, file)
			lats_modified_time = os.path.getmtime(filename)
			new_filename = dir + time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(lats_modified_time))+'.csv'
			if not os.path.exists(new_filename):
				os.rename(filename, new_filename)
	
main()
