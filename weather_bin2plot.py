# -*- coding: utf-8 -*-
"""
Created on 2019.12.11
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

	def gpv_data_coef(self):
		nx, ny, hgt = 720, 361, 12
		elem   = 5 
		return nx, ny, hgt, elem

	def prj_coef(self, nx, ny):
		dx, dy = 0.5, 0.5
		lon, lat = [], []
		for ix in range(nx):
			lon += [ float('{:.2f}'.format(dx*ix)) ]
		for iy in range(ny):
			lat += [ float('{:.2f}'.format(-90. + dy*iy)) ]

		X, Y = np.meshgrid(lon, lat)

		return X, Y

	def preparating_data(self, yyyy, mm, dd, hh):
		time_list = []
		num_time_list = len(time_list)
		
		month_thirtyone = [ 1, 3, 5, 7, 8, 10, 12 ]
		month_thirty    = [ 4, 6, 9, 11 ]
		month_twntynine = [ 2 ]

		while num_time_list < 26:
			time_list.append(str(yyyy) + str('%02d' % mm) + str('%02d' % dd) + str('%02d' % hh) + '00')
			hh = hh - 6
	
			if hh < 0 and dd == 1:
				mm, hh = mm - 1, 18
				if mm in month_thirty:
					dd = 30
				elif mm in month_thirtyone:
					dd = 31
				elif mm in month_twntynine:
					if yyyy % 4 == 0:
						dd = 28
					else:
						dd =29

			elif hh < 0:
				dd, hh = dd - 1, 18

			num_time_list += 1

		return time_list

	def setup_gpv_filelist(self, path, time_list):
		filelist = []
		for i_file in time_list:
			filelist.append(path + '/GSM_Data/' + i_file[0:8] + '/' + i_file[0:10] + '.bin')
		return filelist 

	def open_gpv_filelist(self, gpv_filelist, nx, ny, hgt, elem):
		data = [ []*i for i in range(len(gpv_filelist)) ]
		for num_gpv, gpv_file in enumerate(gpv_filelist):
			with open(gpv_file, 'rb') as ifile:
				"""
				elem: 1-u, 2-v, 3-w, 4-tmp, 5-height
				"""
				data[num_gpv] = np.fromfile(ifile, dtype='>f', sep = '').reshape(elem, hgt, ny, nx)
				print('..... Preparating data for ' + gpv_file, ', shapes :: ', data[num_gpv].shape)
		return data		

	def main_mapping_tool(self, mode, path, time_list, nx, ny, *, gpv_datalist='None', snap_step=0, level='1000'):

		fig, ax = plt.subplots()
		outpath = path + '/Trajectory_GSMData/fig/' 
		
		lat_min, lat_max = 17, 50
		lon_min, lon_max = 120, 155
		
		mapping = Basemap( projection='lcc', resolution="i", lat_0=35, lon_0=140, fix_aspect=(1,1), llcrnrlat=lat_min, urcrnrlat=lat_max, llcrnrlon=lon_min, urcrnrlon=lon_max )

		mapping.drawcoastlines(color='black', linewidth=0.5)
		mapping.drawmeridians(np.arange(0, 360, 5),  labels=[False, True, False, True], fontsize='small', color='gray', linewidth=0.5)
		mapping.drawparallels(np.arange(-90, 90, 5), labels=[True, False, False, True], fontsize='small', color='gray', linewidth=0.5)

		lon_list, lat_list = self.prj_coef(nx, ny)
		x, y = mapping(lon_list, lat_list)

		if mode == 1 or mode == 2:

			if level == "1000":
				hPa, min_list = 0, [0, 200]
			elif level == "925":
				hPa, min_list = 1, [0, 500]
			elif level == "850":
				hPa, min_list = 2, [0, 750]
			elif level == "700":
				hPa, min_list = 3, [0, 1500]
			elif level == "600":
				hPa, min_list = 4, "None"
			elif level == "500":
				hPa, min_list = 5, "None"
			elif level == "400":
				hPa, min_list = 6, "None"
			elif level == "300":
				hPa, min_list = 7, "None"
			elif level == "250":
				hPa, min_list = 8, "None"
			elif level == "200":
				hPa, min_list = 9, "None"
			elif level == "150":
				hPa, min_list = 10, "None"
			elif level == "100":
				hPa, min_list = 11, "None"

			gpv_u_data = gpv_datalist[snap_step][0][hPa]
			gpv_v_data = gpv_datalist[snap_step][1][hPa]
			speed = np.sqrt(gpv_u_data*gpv_u_data + gpv_v_data*gpv_v_data)
			speed_list = list(range(0, 50, 25)) 
		
			gpv_height_data = gpv_datalist[snap_step][4][hPa]
			num_list = list(range(0, 7500, 10))

			contour = mapping.contour(x, y, gpv_height_data, linewidths=0.05, linestyles='-', levels=num_list, colors='m')
			contour.clabel(fmt='%1.1f', fontsize=6.5)

			if not min_list == "None":
				lines = mapping.contourf(x, y, gpv_height_data, min_list, alpha=0.5, hatches=['///'], lw=1., zorder = 0)

			for i_nx, i_ny in itertools.product(range(nx), range(ny)):
				if speed[i_ny][i_nx] > 10 and lon_min <= lon_list[i_ny][i_nx] <= lon_max and lat_min <= lat_list[i_ny][i_nx] <= lat_max:
					print('...... Halfway step, ', i_nx, i_ny, speed[i_ny][i_nx])
					vector = mapping.quiver(x[i_ny][i_nx], y[i_ny][i_nx], gpv_u_data[i_ny][i_nx], gpv_v_data[i_ny][i_nx], color='k', units='dots', scale=2.0, alpha=0.6)
			
			artists, labels = lines.legend_elements()
			
			plt.legend(artists, labels, handleheight=2)
			plt.title(time_list[snap_step] + ' @GSM ' + level + 'hPa' , loc='left', fontsize=10)
			plt.quiverkey(vector, 0.75, 0.9, 10, '10 m/s', labelpos='W', coordinates='figure')

			plt.savefig(outpath + 'GPV_elem_' + time_list[snap_step] + '.png')
			print('...... Saving fig :: ', outpath + 'GPV_elem_' + time_list[snap_step] + '.png')

		#plt.show()

	def main_driver(self, mode, indir, time_list, level):
		nx, ny, hgt, elem = self.gpv_data_coef()

		gpv_filelist = self.setup_gpv_filelist(indir, time_list)
		gpv_datalist = self.open_gpv_filelist(gpv_filelist, nx, ny, hgt, elem)

		if mode == 1:
			snap_step = 0
			self.main_mapping_tool(mode, indir, time_list, nx, ny, gpv_datalist=gpv_datalist, level=level, snap_step=snap_step)
		elif mode == 2:
			for snap_step in range(len(gpv_datalist)):
				self.main_mapping_tool(mode, indir, time_list, nx, ny, gpv_datalist=gpv_datalist, level=level, snap_step=snap_step)

if __name__ == "__main__":
	mapp = mapping()

	#input dir
	indir = '/work3/daichi/MRI/Data/'

	#target time
	yyyy, mm, dd, hh = 2016, 8, 31, 0
	time_list = mapp.preparating_data(yyyy, mm, dd, hh)

	"""
	Target altitude list
	1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100 hPa
	"""
	level = '925' 

	#choose mode, if you append new func. more anynum. 
	"""
	2019.11.12
	mode 1: Normal weather element info at GPV GSM snap shot.
	mode 2: Normal weather element info at GPV GSM gif.
	"""
	
	mode = 2

	#main_driver
	mapp.main_driver(mode, indir, time_list, level)

