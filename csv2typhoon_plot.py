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

	def setup_csv_filelist(self, path, time_list, ft_grd):
		filelist = []
		filelist = glob.glob(path + 'table' + '*.csv')
		return filelist

	def open_csv_filelist(self, csv_filelist):
		csv_datalist = []
		list_option = ( 'year', 'month', 'day', 'hour(UTC)', 'typhoon number', 'typhoon name', 'rank','latitude', 'longinitude', 'central pressure', 'max wind')
		for num_file, infile in enumerate(trajectory_filelist):
			tmp_data = pd.read_csv(infile, usecols=[0:10], skiprows=1, names=list_option)
			print(tmp_data)
			tmp_list = tmp_data.values.tolist()
			csv_datalist.extend(tmp_list)
			print('..... Preparating data for ' + str(num_file) + ' ' + str(infile))
		return trajectory_ondatalist

	def main_driver(self, indir)

if __name__ == "__main__":
	mapp = mapping()

	#input dir
	indir = '/work3/daichi/MRI/Data/typhoon_csv'

	#typhoon target name
	typhoon_num = [1919, 1921]

	#main_driver
	mapp.main_driver(indir, typhoon_num)

	print('Normal END')




