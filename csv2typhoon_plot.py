# -*- coding: utf-8 -*-
"""
Created on 2019.12.5
@author: Toyooka
"""

import numpy as np
import pandas as pd
import glob
import itertools
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap

class mapping:

	def __init__(self):
		pass

	def setup_csv_filelist(self, path):
		filelist = []
		filelist = glob.glob(path + '*.csv')
		return filelist

	def open_csv_filelist(self, csv_filelist):
		csv_datalist = [ []*i for i in range(len(csv_filelist)) ]
		list_num = list(range(11)) 
		list_option = ( 'year', 'month', 'day', 'hour(UTC)', 'typhoon number', 'typhoon name', 'rank','latitude', 'longinitude', 'central pressure', 'max wind')
		for num_file, infile in enumerate(csv_filelist):
			tmp_data = pd.read_csv(infile, usecols=list_num, skiprows=1, names=list_option, sep=',')
			tmp_list = tmp_data['latitude'].values.tolist()
			csv_datalist[num_file].extend(tmp_list)
			print('..... Preparating data for ' + str(num_file) + ' ' + str(infile))
		return csv_datalist

	def main_driver(self, indir, typhoon_num):
		csv_filelist = self.setup_csv_filelist(indir)
		csv_datalist = self.open_csv_filelist(csv_filelist)
		print(csv_datalist[0])

if __name__ == "__main__":
	mapp = mapping()

	#input dir
	indir = '/work3/daichi/MRI/Data/typhoon_csv/'

	#typhoon target name
	typhoon_num = [1919, 1921]

	#main_driver
	mapp.main_driver(indir, typhoon_num)

	print('Normal END')




