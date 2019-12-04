# -*- coding: utf-8 -*-
"""
Created on 2019.11.25
@author: Toyo_Daichi
"""

import numpy as np
import pandas as pd
import glob
import itertools
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap

#import warnings;warnings.filterwarnings('ignore')

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

		while num_time_list < 13:
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

	def setup_trajectory_filelist(self, path, target_time, altitude):
		filelist = []
		filelist = glob.glob(path + '/Trajectory_GSMData/' + target_time + '/' + str(altitude) + 'm' + '/particle_*.data')
		return filelist

	def open_typhoon_filelist(self, trajectory_filelist):
		trajectory_datalist = []
		list_option = ['Lon(deg)', 'Lat(deg)', 'H.absl(m)']
		for num_file, infile in enumerate(trajectory_filelist):
			tmp_data = pd.read_csv(infile, usecols=list_option, delimiter='\s+')
			tmp_list = tmp_data.values.tolist()
			trajectory_datalist.extend(tmp_list)
			print('..... Preparating data for ' + str(infile))
		return trajectory_datalist

	def Toformat_data(self, trajectory_datalist, num_of_filelist, num_of_particle, trajectory_step):
		print('.....   1st. Shapes  ::  ', len(trajectory_datalist))
		print('.....   2nd. Shapes  ::  ', len(trajectory_datalist[0]))
		print('.....   Check length ::  all trajectory step, get trajectory length')
		print('                       ', trajectory_step*num_of_filelist, len(trajectory_datalist))
		
		trajectory_lon_list  = list(map(lambda x: x[0], trajectory_datalist))
		trajectory_lat_list  = list(map(lambda x: x[1], trajectory_datalist))
		trajectory_high_list = list(map(lambda x: x[2], trajectory_datalist))

		particle_lon_data  = [ []*i for i in range(num_of_filelist) ]
		particle_lat_data  = [ []*i for i in range(num_of_filelist) ]
		
		for i_particle, i_trajectory_step in itertools.product(range(num_of_filelist), range(trajectory_step)):
			j_trajectory_step = trajectory_step*i_particle + i_trajectory_step
			
			particle_lon_data[i_particle].append(  float('{:.8f}'.format(trajectory_lon_list[j_trajectory_step]) ))		
			particle_lat_data[i_particle].append(  float('{:.7f}'.format(trajectory_lat_list[j_trajectory_step]) ))

		return particle_lon_data, particle_lat_data

	def main_mapping_tool(self, mode, path, time_list, nx, ny, *, gpv_datalist='None', particle_lon_data='None', particle_lat_data='None', snap_step=0, altitude='500', num_of_filelist=99):

		fig, ax = plt.subplots()
		outpath = path + '/Trajectory_GSMData/fig/' 

		map = Basemap( projection='lcc', resolution="i", lat_0=35, lon_0=140, fix_aspect=(1,1),
									 llcrnrlat=17, urcrnrlat=50, llcrnrlon=120, urcrnrlon=155 )

		map.drawcoastlines(color='black', linewidth=0.5)
		map.drawmeridians(np.arange(0, 360, 5),  labels=[False, True, False, True], fontsize='small', color='gray', linewidth=0.5)
		map.drawparallels(np.arange(-90, 90, 5), labels=[True, False, False, True], fontsize='small', color='gray', linewidth=0.5)

		lon_list, lat_list = self.prj_coef(nx, ny)
		x, y = map(lon_list, lat_list)

		if altitude == '500':
			level, hPa = 1, '925'
		elif altitude == '2500':
			level, hPa = 3, '700'
		elif altitude == '5000':
			level, hPa = 5, '500'
		else:
			level, hPa = 0, '1000' 

		if mode == 1 or mode == 2:

			num_list = list(range(0, 7500, 25))	

			if snap_step < 2:
				gpv_data, hr = gpv_datalist[0], '0-6'
			elif snap_step < 5:
				gpv_data, hr = gpv_datalist[1], '6-12'
			elif snap_step < 7:
				gpv_data, hr = gpv_datalist[2], '12-18'
			elif snap_step < 9:
				gpv_data, hr = gpv_datalist[3], '18-24'
			elif snap_step < 11:
				gpv_data, hr = gpv_datalist[4], '24-30'
			elif snap_step < 13:
				gpv_data, hr = gpv_datalist[5], '30-36'
			elif snap_step < 15:
				gpv_data, hr = gpv_datalist[6], '36-42'
			elif snap_step < 17:
				gpv_data, hr = gpv_datalist[7], '42-48'
			elif snap_step < 19:
				gpv_data, hr = gpv_datalist[8], '48-54'
			elif snap_step < 21:
				gpv_data, hr = gpv_datalist[9], '54-60'
			elif snap_step < 23:
				gpv_data, hr = gpv_datalist[10], '60-66'
			elif snap_step < 25:
				gpv_data, hr = gpv_datalist[11], '66-72'

			contour = map.contour(x, y, gpv_data[4][level], linestyles=':', colors='k', alpha=0.8, levels=num_list)
			contour.clabel(fmt='%1.1f', fontsize=8)

			map_lon_data  = [ []*i for i in range(num_of_filelist) ]
			map_lat_data  = [ []*i for i in range(num_of_filelist) ]
					
			for i_particle in range(num_of_filelist):
				map_lon_data[i_particle], map_lat_data[i_particle] = map(particle_lon_data[i_particle], particle_lat_data[i_particle])
			for i_particle in range(num_of_filelist):
				map.plot(map_lon_data[i_particle][0:snap_step +1], map_lat_data[i_particle][0:snap_step +1], linewidth=0.5, color='c', ls='--', marker='o', ms=2)

			plt.title('96hr conduct from ' + time_list[0] + ', step :: ' + str(snap_step) + ', hour :: ' + hr, loc='left', fontsize=10)
			fig.suptitle('Isobaric Backward Trajectory ' + str(hPa) + 'hPa @GSM', x=0.45, y=0.98, fontsize=12)
		
			if snap_step < 10:
				plt.savefig(outpath + 'Isobaric_Backward_trajectory_' + time_list[0] + '_' + str(altitude) + 'm_0' + str(snap_step)  + 'step.png')
				print('...... Saving fig :: ', 'Isobaric_Backward_trajectory_' + time_list[0] + '_'+ str(altitude) + 'm_0' + str(snap_step) + 'step.png') 
			else:			
				plt.savefig(outpath + 'Isobaric_Backward_trajectory_' +time_list[0] + '_' + str(altitude) + 'm_' + str(snap_step)  + 'step.png')
				print('...... Saving fig :: ', 'Isobaric_Backward_trajectory_' + time_list[0] + '_'+ str(altitude) + 'm_' + str(snap_step) + 'step.png') 

		elif mode == 3:
			x, y = map(particle_lon_data, particle_lat_data)
			map.hexbin(np.array(x), np.array(y), gridsize=[20, 20], cmap='Blues', edgecolors='gray', mincnt=8)	
			plt.title('96hr conduct from ' + time_list[0] , loc='left', fontsize=10)
			fig.suptitle('Isobaric Backward Trajectory strength.' + 'all m @GSM', fontsize=12)

			plt.savefig(outpath + 'Isobaric_Backward_strength_' + time_list[0] + '.png')
			print('...... Saving fig :: ', outpath + 'Isobaric_Backward_strength_' + time_list[0] + '.png')


		elif mode == 4 or mode == 5:
			gpv_u_data = gpv_datalist[snap_step][0][level]
			gpv_v_data = gpv_datalist[snap_step][1][level]
			gpv_height_data = gpv_datalist[snap_step][4][level]
			speed = np.sqrt(gpv_u_data*gpv_u_data + gpv_v_data*gpv_v_data)
		
			num_list = list(range(0, 7500, 10))	
			speed_list = list(range(0, 50, 25)) 
			color_list=['w','k']

			contour = map.contour(x, y, gpv_height_data, linewidths=0.05, linestyles='-', alpha=1.0, levels=num_list, colors='k')
			contour.clabel(fmt='%1.1f', fontsize=8)

			for i_nx, i_ny in itertools.product(range(nx), range(ny)):
				if speed[i_ny][i_nx] > 10 and lon_list[i_ny][i_nx] > 120 and lat_list[i_ny][i_nx] > 20:
					print('...... Halfway step, ', i_nx, i_ny, speed[i_ny][i_nx])
					vector = map.quiver(x[i_ny][i_nx], y[i_ny][i_nx], gpv_u_data[i_ny][i_nx], gpv_v_data[i_ny][i_nx], color='k', units='dots', scale=2.0) 
			plt.quiverkey(vector, 0.75, 0.9, 10, '10 m/s', labelpos='W', coordinates='figure')
			
			plt.title(time_list[snap_step] + ' @GSM ' + altitude + 'm' , loc='left', fontsize=10)

			plt.savefig(outpath + 'GPV_Height' + time_list[snap_step] + '.png')
			print('...... Saving fig :: ', outpath + 'GPV_Height' + time_list[snap_step] + '.png')


		#plt.show()

	def main_driver(self, mode, indir, time_list, altitude, trajectory_step, num_of_particle):
		nx, ny, hgt, elem = self.gpv_data_coef()
		if mode == 1 or mode == 2:

			gpv_filelist = self.setup_gpv_filelist(indir, time_list)
			gpv_datalist = self.open_gpv_filelist(gpv_filelist, nx, ny, hgt, elem)

			trajectory_filelist = self.setup_trajectory_filelist(indir, time_list[0], altitude)
			trajectory_datalist = self.open_trajectory_filelist(trajectory_filelist)
			num_of_filelist     = len(trajectory_filelist)

			particle_lon_data, particle_lat_data = self.Toformat_data(trajectory_datalist, num_of_filelist, num_of_particle, trajectory_step)

			if mode == 1:
				snap_step = trajectory_step
				self.main_mapping_tool(mode, indir, time_list, nx, ny, gpv_datalist=gpv_datalist, particle_lon_data=particle_lon_data, particle_lat_data=particle_lat_data, snap_step=snap_step, altitude=altitude, num_of_filelist=num_of_filelist)

			elif mode == 2:
				for snap_step in range(trajectory_step):
					self.main_mapping_tool(mode, indir, time_list, nx, ny, gpv_datalist=gpv_datalist, particle_lon_data=particle_lon_data, particle_lat_data=particle_lat_data, snap_step=snap_step, altitude=altitude, num_of_filelist=num_of_filelist)

		elif mode == 3:
			trajectory_filelist = self.setup_trajectory_filelist(indir, time_list[0], altitude)
			trajectory_datalist = self.open_trajectory_filelist(trajectory_filelist)
			num_of_filelist     = len(trajectory_filelist)

			particle_lon_data, particle_lat_data = self.Toformat_data(trajectory_datalist, num_of_filelist, num_of_particle, trajectory_step)

			particle_lon_data = list(itertools.chain.from_iterable(particle_lon_data))
			particle_lat_data = list(itertools.chain.from_iterable(particle_lat_data))

			self.main_mapping_tool(mode, indir, time_list, nx, ny, particle_lon_data=particle_lon_data, particle_lat_data=particle_lat_data, altitude=altitude, num_of_filelist=num_of_filelist)

		elif mode == 4 or mode == 5:
			gpv_filelist = self.setup_gpv_filelist(indir, time_list)
			gpv_datalist = self.open_gpv_filelist(gpv_filelist, nx, ny, hgt, elem)

			if mode == 4:
				snap_step = 0
				self.main_mapping_tool(mode, indir, time_list, nx, ny, gpv_datalist=gpv_datalist, altitude=altitude, snap_step=snap_step)
			elif mode == 5:
				for snap_step in range(len(gpv_datalist)):
					self.main_mapping_tool(mode, indir, time_list, nx, ny, gpv_datalist=gpv_datalist, altitude=altitude, snap_step=snap_step)

if __name__ == "__main__":
	mapp = mapping()

	#input dir
	indir = '/work3/daichi/MRI/Data/'

	#target time
	yyyy, mm, dd, hh = 2018, 7, 8, 0
	time_list = mapp.preparating_data(yyyy, mm, dd, hh)

	#target altitude
	altitude = '500' 
	#altitude_list = ['500', '2500', '5000', or '*']

	#particle info
	trajectory_step, num_of_particle = 24, 99

	#choose mode, if you append new func. more anynum. 
	"""
	2019.11.12
	mode 1: trajectory plot and contour snap shot.
	mode 2: trajectory plot and contour gif.
	mode 3: trajectory plot hexbin.
	mode 4: Normal weather element info at GPV GSM snap shot.
	mode 5: Normal weather element info at GPV GSM gif.
	"""
	
	mode = 5

	#main_driver
	mapp.main_driver(mode, indir, time_list, altitude, trajectory_step, num_of_particle)

