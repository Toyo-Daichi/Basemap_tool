# -*- coding: utf-8 -*-
"""
Created on 2019.12.5
@author: Toyo_Daichi
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

	def setup_csv_filelist(self, path, *, year='*'):
		filelist = []
		filelist = glob.glob(path + 'table' + str(year) + '.csv')
		return filelist

	def open_csv_filelist(self, csv_filelist):
		csv_datalist = [ []*i for i in range(len(csv_filelist)) ]
		list_num     = list(range(11)) 
		list_option  = ( 'year', 'month', 'day', 'hour(UTC)', 'typhoon number', 'typhoon name', 'rank','latitude', 'longitude', 'central pressure', 'max wind')
		for num_file, infile in enumerate(csv_filelist):
			print('..... Preparating data for ' + str(num_file) + ' ' + str(infile))
			tmp_data = pd.read_csv(infile, usecols=list_num, skiprows=1, names=list_option, sep=',')
			tmp_lat_list  = tmp_data['latitude'].values.tolist()
			csv_datalist[num_file].append(tmp_lat_list)
			tmp_lon_list = tmp_data['longitude'].values.tolist()
			csv_datalist[num_file].append(tmp_lon_list)
			tmp_centpre_list = tmp_data['central pressure'].values.tolist()
			csv_datalist[num_file].append(tmp_centpre_list)
		return csv_datalist

	def main_mapping_tool(self, path, csv_datalist, csv_specific_datalist='None'):
		fig, ax = plt.subplots()
		outpath = path + '/fig/' 

		map = Basemap( projection='lcc', resolution="i", lat_0=35, lon_0=140, fix_aspect=(1,1), llcrnrlat=17, urcrnrlat=50, llcrnrlon=120, urcrnrlon=155 )

		map.drawcoastlines(color='black', linewidth=0.5)
		map.drawmeridians(np.arange(0, 360, 5),  labels=[False, True, False, True], fontsize='small', color='gray', linewidth=0.5)
		map.drawparallels(np.arange(-90, 90, 5), labels=[True, False, False, True], fontsize='small', color='gray', linewidth=0.5)

		full_lon_list  = np.array(list(map(lambda x: x[0], trajectory_ondatalist))).flatten()
		full_lat_list  = np.array(list(map(lambda x: x[1], trajectory_ondatalist))).flatten()
		
		x, y = map(full_lon_list, full_lat_list)
		
		hexbin = map.hexbin(np.array(x), np.array(y), gridsize=[20, 20], cmap='Blues', edgecolors='gray', mincnt=3)
		cbar = plt.colorbar(hexbin, extend='max')
		cbar.set_label(r'number', fontsize=8)

		if not csv_specific_datalist == "None":
			case_x, case_y = map(csv_specific_datalist[0], csv_specific_datalist[1])
			map.plot(case_x, case_y, linewidth=0.5, color='c', ls='--', marker='o', ms=2)
			map.scatter(case_x, case_y, s=csv_specific_datalist[2], c="pink", alpha=0.5, linewidths="2", edgecolors="red")
			for text_num, i_text in emmurate(csv_specific_datalist[2]):
				map.text(case_x[text_num], case_y[text_num], 'SLP' + i_text)

		plt.title('Course of typhoon 2000-2019', loc='left', fontsize=10)
		plt.show()

	def main_driver(self, indir, *, typhoon_info='None'):
		csv_filelist = self.setup_csv_filelist(indir)
		csv_datalist = self.open_csv_filelist(csv_filelist)
		"""
		csv_datalist.shape = [year][latitude][longitude][central_pressure]
		"""

		if not typhoon_info == "None": 
			print()
			print('..... check specific case filelist')
			csv_specific_filelist = self.setup_csv_filelist(indir, year=typhoon_info[0])
			csv_specific_datalist = self.open_csv_filelist(csv_specific_filelist)
			self.main_mapping_tool(indir, csv_datalist, csv_specific_datalist=csv_specific_datalist)
		else:
			self.main_mapping_tool(indir, csv_datalist)

if __name__ == "__main__":
	mapp = mapping()

	#input dir
	indir = '/work3/daichi/MRI/Data/typhoon_csv/'

	"""
	If you want to write a specific typhoon route, enter the typhoon information.
	typhoon_info = [year, typhoon_number]
	"""
	typhoon_info = [2018, 1810]

	#main_driver
	mapp.main_driver(indir, typhoon_info=typhoon_info)

	print('Normal END')
