#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 16:39:17 2021

@author: sydneydybing
"""

def noise_picker(stas, dates, samples_per_cpu, noise_data_path, write_sample_path, cpu_number, save_npy_path, save_npy_name, progress_report_path):

    # Pick first a random station from the list in the directory, then a random
    # day, and then a random 384 second timespan of noise from the mseed file.
    # Avoid picking times when earthquakes occurred. 
    
    from obspy import read,Stream,UTCDateTime
    import numpy as np
    from glob import glob
    import matplotlib.pyplot as plt
    import random
    
    i = 0 # Counter to get enough noise records

    data_list = []
    
    w = open(progress_report_path + 'CPU_' + str(cpu_number) + '_progress_report.txt', 'w')
    
    while i < samples_per_cpu:
        
        try: 
            
            random_sta = random.choice(stas)
            # print(random_sta)
            # random_sta = 'ACSX'
            
            stas_in_folder = glob(noise_data_path + '*/')
            # print(stas_in_folder)
            
            # Checking if the random station chosen exists    
        
            if noise_data_path + str(random_sta) + '/' in stas_in_folder:
                # print(str(random_sta) + ' is there')
                
                # If it does exist, choose a random date
                random_date = random.choice(dates)
                # print(random_date)
                # random_date = '20190713'
                
                # Make sure it's not one of the earthquake days
                    
                if random_date == '20190704' or random_date == '20190705' or random_date == '20190706' or random_date == '20190707' or random_date == '20190712' or random_date == '20190716' or random_date == '20190726' or random_date == '20190822' or random_date == '20190823' or random_date == '20200604':
                    print(str(random_date) + ' gets skipped - earthquake day')
                    
                else:
                
                    dates_in_folder = glob(noise_data_path + str(random_sta) + '/' + str(random_sta) + '.u.*.mseed')
                    # print(dates_in_folder)
                    
                    # Checking if the random date chosen exists
                    if noise_data_path + str(random_sta) + '/' + str(random_sta) + '.u.' + str(random_date) + '.mseed' in dates_in_folder:
                        # print(str(random_date) + ' is there')
                        
                        # If it does exist, choose a random 384 second timespan
                        e = read(noise_data_path + str(random_sta) + '/' + str(random_sta) + '.e.' + str(random_date) + '.mseed')
                        n = read(noise_data_path + str(random_sta) + '/' + str(random_sta) + '.n.' + str(random_date) + '.mseed')
                        u = read(noise_data_path + str(random_sta) + '/' + str(random_sta) + '.u.' + str(random_date) + '.mseed')
                        
                        # e.plot()
                        # n.plot()
                        # u.plot()
                        
                        # Need to check for gaps and make sure not to pick those
                        
                        times = e[0].times()
                        # print(times)
                        # data = e[0].data
                        # print(data)
                        
                        try:
                            
                            # The latest time in the array for which we could still get a 384 second sample
                            latest_time = times[-256] # 384 if one long noise section
                            # print('Latest time: ' + str(latest_time))
                            
                            start_time = random.choice(times)
                            # print('Start time: ' + str(start_time))
                            
                            if start_time <= latest_time:
                                # print('Good start time')
                                
                                end_time = start_time + 255 # 383 if one long noise section rather than 3
                                # print('End time: ' + str(end_time))
                                
                                # Then grab the section of data and save it as its own mseed
                                st_start_time = e[0].stats.starttime
                                # print(st_start_time)
                                UTC_random_start_time = st_start_time + start_time
                                # print(UTC_random_start_time)
                                UTC_end_time = UTC_random_start_time + 255
                                # print(UTC_end_time)
                                
                                # random_write_counter
                                iout = np.random.randint(0,10000) # between 0 and 1000
                                
                                # Trim and normalize the data
                                e_trim = e.trim(UTC_random_start_time, UTC_end_time)
                                # e_trim.plot()
                                e_demean = e_trim.detrend(type='demean')
                                # e_demean.plot()
                                # e_demean.write(write_sample_path + str(cpu_number) + '_' + str(random_sta) + '.e.' + str(random_date) + '.' + str(iout) + '.noise.mseed', format='MSEED')
                                # print(e_demean[0].stats.npts)
                                
                                n_trim = n.trim(UTC_random_start_time, UTC_end_time)
                                # n_trim.plot()
                                n_demean = n_trim.detrend(type='demean')
                                # n_demean.plot()
                                # n_demean.write(write_sample_path + str(cpu_number) + '_' + str(random_sta) + '.n.' + str(random_date) + '.' + str(iout) + '.noise.mseed', format='MSEED')
                                # print(n_demean[0].stats.npts)
                                
                                u_trim = u.trim(UTC_random_start_time, UTC_end_time)
                                # u_trim.plot()
                                u_demean = u_trim.detrend(type='demean')
                                # u_demean.plot()
                                # u_demean.write(write_sample_path + str(cpu_number) + '_' + str(random_sta) + '.u.' + str(random_date) + '.' + str(iout) + '.noise.mseed', format='MSEED')
                                # print(u_demean[0].stats.npts)
                                
                                # Combine all three into one array to match length of data arrays and save the .npy
                                e_data = e_demean[0].data
                                n_data = n_demean[0].data
                                u_data = u_demean[0].data
                                
                                comb_data = np.append(n_data, e_data)
                                comb_data = np.append(comb_data, u_data) # Order: N, E, Z(U)
                                
                                # plt.figure()
                                # plt.title(random_sta + '_' + random_date)
                                # plt.plot(comb_data)
                                # plt.xlabel('Time (s)')
                                # plt.ylabel('Displacement (m)')
                                # plt.xlim(0,383)
                                # plt.show()
                                # plt.close()
                                
                                data_list.append(comb_data)
                                
                                print('--------------------------')
                                
                                print('Success: station ' + str(random_sta) + ' for ' + str(random_date))
                                
                                i += 1
                                print(i)
                                
                                line = '%s\n'%(i)
                                # print(line)
                                w.write(line)
                                
                                print('--------------------------')
                            
                            else:
                                ('Station ' + str(random_sta) + ' for date ' + str(random_date) + ': not enough samples')
                        
                        except:
                            print('Station ' + str(random_sta) + ' for date ' + str(random_date) + ': time pick failed')
                        
                    else:
                        print('Date ' + str(random_date) + ' is not there for station ' + str(random_sta))
                
            else:
                print('Station ' + str(random_sta) + ' is not there')
                
        except:
            print('Unknown error: station ' + str(random_sta) + ' for date ' + str(random_date))
    
    w.close()
    
    # Currently the picker fails if there's a day of data selected that has gaps I think   
    # Failure examples to look at: Station ACSX for date 20200213: time pick failed, Station BBDM for date 20190901: time pick failed
    
    data_array = np.array(data_list)
    print(data_array.shape)
    
    np.save(save_npy_path + 'CPU_' + str(cpu_number) + '_' + save_npy_name, data_array)
    # np.save(save_npy_path + save_npy_name, data_array)
    
    
    
    