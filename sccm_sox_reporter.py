#!/usr/bin/env python3

# This file will grab required data from SCCM reports and create Data.csv file for SOX reporting
# v2 27.09.2017 (c) Artem Ageev

import os
import sys
import csv
import time, datetime
import operator


LOG_DIR = '/logs/'
DATA_DIR = '/SCCM daily reports/'


COUNTRY_LIST = ['']

def main():

	rename_files(LOG_DIR)
	build_data_file(DATA_DIR, LOG_DIR)


def build_data_file(dir, logs): #will build (or append if exists) data.csv file based on logs from "Logs" dir
	patch_data =[]
	country_dict = {}

	# build empty dict based on country list:
	for subdir, dirs, files in os.walk(logs):
		for file in files:
			daily_data = {}
			daily_list = []
			
			#create empty country_dict. will me used as template
			for i in COUNTRY_LIST:
				country_dict[i] = [0, 0]

			#read data
			filename = os.path.join(subdir, file)

			with open(filename) as f:
				raw_data = list(csv.reader(f.readlines(), delimiter=',', dialect='excel')) 
			
			data = get_data(raw_data) # extract interesting patch data from the file

			# build daily data dict. 1st value will be used as a dict key
			for i in data:
				daily_data[i[0]] = [i[1], i[9].replace(".", ",")] #replace "." with "," for correct EXCEL handling

			country_dict.update(daily_data) # concatinate template dict with daily dict 

			daily_list.append(time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(filename))))

			# build simple list to work with
			for i in sorted(country_dict.items()):
				daily_list.append(i[1][0])
				daily_list.append(i[1][1])

			patch_data.append(daily_list)

#	sort data. For some reasons its not sorted sometimes
	patch_data = sorted(patch_data, key=operator.itemgetter(0), reverse=False)

	write_data(patch_data)

def write_data(patch_data):
	with open(DATA_DIR + 'data.csv', "w", newline='') as f:
		writer = csv.writer(f, delimiter=';')
		writer.writerows(patch_data)

def rename_files(dir): #will rename all files in DIR according to Last Modified file time property
	for subdir, dirs, files in os.walk(dir):
		for file in files:
			filename = os.path.join(subdir, file)
			lats_modified_time = os.path.getmtime(filename)
			new_filename = dir + time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(lats_modified_time))+'.csv'
			if not os.path.exists(new_filename):
				os.rename(filename, new_filename)

def get_data(raw_data):
	ptr_end = 0
	for i in raw_data:
		if i == ['CC', 'Count', 'Laptops', 'Desktops', 'Virtuals', 'SCCM__', 'MBAM__', 'McAfee__', 'AppV__', 'Patch__', 'Boot__', 'HDD__']:
			ptr_start = raw_data.index(i) + 1
		try:
			if i[0] == 'Count1':
				ptr_end = raw_data.index(i) - 1
		except:
			pass
	return(raw_data[ptr_start:ptr_end])


main()
