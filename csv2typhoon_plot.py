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

	def open_csv_filelist(self, csv_filelist, *, typhoon_number='None'):
		csv_datalist = [ []*i for i in range(len(csv_filelist)) ]
		list_num     = list(range(11)) 
		list_option  = ( 'year', 'month', 'day', 'hour(UTC)', 'typhoon_number', 'typhoon_name', 'rank','latitude', 'longitude', 'central_pressure', 'max_wind')
		for num_file, infile in enumerate(csv_filelist):
			print('..... Preparating data for ' + str(num_file) + ' ' + str(infile))
			tmp_data = pd.read_csv(infile, usecols=list_num, skiprows=1, names=list_option, sep=',')
			if typhoon_number == "None":
				tmp_lat_list  = tmp_data['latitude'].values.tolist()
				csv_datalist[num_file].append(tmp_lat_list)
				tmp_lon_list = tmp_data['longitude'].values.tolist()
				csv_datalist[num_file].append(tmp_lon_list)
				tmp_centpre_list = tmp_data['central_pressure'].values.tolist()
				csv_datalist[num_file].append(tmp_centpre_list)

			else:
				csv_datalist = []
				specific_data = tmp_data.query('typhoon_number == %s' % typhoon_number) 
				tmp_lat_list  = specific_data['latitude'].values.tolist()
				csv_datalist.append(tmp_lat_list)
				tmp_lon_list = specific_data['longitude'].values.tolist()
				csv_datalist.append(tmp_lon_list)
				tmp_centpre_list = specific_data['central_pressure'].values.tolist()
				csv_datalist.append(tmp_centpre_list)

		return csv_datalist

	def main_mapping_tool(self, path, csv_datalist, csv_specific_datalist='None'):
		fig, ax = plt.subplots()
		outpath = path + '/fig/' 

		lat_min, lat_max = 17, 50
		lon_min, lon_max = 120, 155

		mapping = Basemap( projection='lcc', resolution="i", lat_0=35, lon_0=140, fix_aspect=(1,1), llcrnrlat=lat_min, urcrnrlat=lat_max, llcrnrlon=lon_min, urcrnrlon=lon_max )

		mapping.drawcoastlines(color='black', linewidth=0.5)
		mapping.drawmeridians(np.arange(0, 360, 5),  labels=[False, True, False, True], fontsize='small', color='gray', linewidth=0.5)
		mapping.drawparallels(np.arange(-90, 90, 5), labels=[True, False, False, True], fontsize='small', color='gray', linewidth=0.5)

		full_lat_list  = list(map(lambda x: x[0], csv_datalist))
		full_lon_list  = list(map(lambda x: x[1], csv_datalist))
	
		full_lat_list = np.sum(full_lat_list, axis=0)
		full_lon_list = np.sum(full_lon_list, axis=0)
		
		lat_list, lon_list = [], []
		for i_num in range(len(full_lat_list)):
			if(lat_min <= full_lat_list[i_num] <= lat_max and lon_min <= full_lon_list[i_num] <= lon_max):
				lat_list.append(full_lat_list[i_num])	
				lon_list.append(full_lon_list[i_num])	

		x, y = mapping(lon_list, lat_list)
		hexbin = mapping.hexbin(np.array(x), np.array(y), gridsize=[30, 30], cmap='Blues', edgecolors='gray', mincnt=8)

		if not csv_specific_datalist == "None":
			specific_lat_list, specific_lon_list = csv_specific_datalist[0], csv_specific_datalist[1]
			specific_centpre_list = csv_specific_datalist[2]

			lat_list, lon_list, centpre_list = [], [], []
			for i_num in range(len(specific_lon_list)):
				if(lat_min <= specific_lat_list[i_num] <= lat_max and lon_min <= specific_lon_list[i_num] <= lon_max):
					lat_list.append(specific_lat_list[i_num])
					lon_list.append(specific_lon_list[i_num])	
					centpre_list.append(specific_centpre_list[i_num])	

			case_x, case_y = mapping(lon_list, lat_list)
			#mapping.plot(case_x, case_y, linewidth=0.5, color='c', ls='--', marker='o', ms=2)
			mapping.plot(np.array(case_x), np.array(case_y))
			mapping.scatter(case_x, case_y, s=centpre_list, c="pink", alpha=0.5, linewidths="2", edgecolors="red")
		#	for text_num, i_text in enumerate(centpre_list):
		#		plt.text(case_x[text_num], case_y[text_num], 'SLP: ' + str(i_text))

		cbar = plt.colorbar(hexbin, extend='max')
		cbar.set_label(r'number', fontsize=8)
		plt.title('Course of typhoon 2000-2019', loc='left', fontsize=10)
		plt.show()

	def main_driver(self, indir, *, typhoon_info='None'):
		csv_filelist = self.setup_csv_filelist(indir)
		csv_datalist = self.open_csv_filelist(csv_filelist)
		"""
		csv_datalist.shape = [year][latitude][longitude][central_pressure]
		"""

		if not typhoon_info == "None": 
			print('..... Check specific case filelist')
			csv_specific_filelist = self.setup_csv_filelist(indir, year=typhoon_info[0])
			csv_specific_datalist = self.open_csv_filelist(csv_specific_filelist, typhoon_number=typhoon_info[1])
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
	typhoon_info = [2016, 1610]

	#main_driver
	mapp.main_driver(indir, typhoon_info=typhoon_info)

	print('Normal END')
