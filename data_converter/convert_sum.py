import h5py
from nilm_metadata import convert_yaml_to_hdf5
from nilmtk import DataSet
from nilmtk.datastore import Key
from nilmtk.utils import get_datastore
from nilmtk.measurement import LEVEL_NAMES
import matplotlib.pyplot as plot
import nilmtk
import os
import numpy as np
import pandas as pd
import pprint
import warnings
warnings.filterwarnings("ignore")

BASE_DIR = '../BLOND/BLOND-250'


"""Gets all summery data for one Medal (= six sockets).
Args:
    medalIndex(Int): MEDAL number the data to get.
Returns:
     A list of all six pandas frames, one for each sockets.
"""

def get_summary_data(medalindex):
    frames_array = [[], [], [], [], [], []]
    for date_folder in os.listdir(BASE_DIR):
        date_dir = os.path.join(BASE_DIR, date_folder)
        for medal_folder in os.listdir(date_dir):
            if medal_folder == 'medal-' + str(medalindex):
                medal_dir = os.path.join(date_dir, medal_folder)
                for medal_file_name in os.listdir(medal_dir):
                    if 'summary' in medal_file_name:
                        filename = os.path.join(medal_dir, medal_file_name)
                        file = h5py.File(filename)
                        for i in range(1, 7):
                            data = {
                              ('current', ''): file['current_rms'+str(i)],
                              ('voltage', ''): file['voltage_rms'], 
                              ('power', 'apparent'): file['apparent_power'+str(i)], 
                              ('power', 'active'): file['real_power'+str(i)]
                            }
                            frame = pd.DataFrame(data=data)
                            frame.columns.set_names(LEVEL_NAMES, inplace=True)
                            frames_array[i-1].append(frame)

    for i in range(0, 6):
        frames_array[i] = pd.concat(frames_array[i])
        frames_array[i].index = get_time_array(len(frames_array[i]), True)
        frames_array[i].index = pd.to_datetime(
            frames_array[i].index.values, unit='s', utc=True)
        frames_array[i] = frames_array[i].tz_convert('Europe/Berlin')

    return frames_array


"""Gets all summery data for the CLEAR meter.
Args:
   -
Returns:
     A list of all three pandas frames, one for each circuit.
"""

def get_clear_data():
  frames_array = [[], [], []]
  for date_folder in os.listdir(BASE_DIR):
    date_dir = os.path.join(BASE_DIR, date_folder)
    for clear_folder in os.listdir(date_dir):
      if clear_folder == 'clear':
        medal_dir = os.path.join(date_dir, clear_folder)
        for clear_file_name in os.listdir(medal_dir):
          if 'summary' in clear_file_name:
            filename = os.path.join(medal_dir, clear_file_name)
            file = h5py.File(filename)
            for i in range(1, 4):
              data = {
                ('current', ''): file['current_rms'+str(i)], 
                ('voltage', ''): file['voltage_rms'+str(i)], 
                ('power', 'apparent'): file['apparent_power'+str(i)], 
                ('power', 'active'): file['real_power'+str(i)]}
              frame = pd.DataFrame(data=data)
              frame.columns.set_names(LEVEL_NAMES, inplace=True)
              frames_array[i-1].append(frame)

  for i in range(0, 3):
    frames_array[i] = pd.concat(frames_array[i])
    frames_array[i].index = get_time_array(len(frames_array[i]), False)
    frames_array[i].index = pd.to_datetime(
        frames_array[i].index.values, unit='s', utc=True)
    frames_array[i] = frames_array[i].tz_convert('Europe/Berlin')

  return frames_array


"""Gets all summery data for the CLEAR meter.
Args:
   num_rows(Int): Determines the length of the array.
   isMedal(Bool): Choses between CLEAR and MEDAL start time.
Returns:
     A list with length num_rows starting at chosen time point.
"""

def get_time_array(num_rows, isMedal):
    if isMedal:
        START_DATE = np.datetime64(
            '2017-05-12T11:08:28') - np.timedelta64('2', 'h')
    else:
        START_DATE = np.datetime64(
            '2017-05-12T11:08:46') - np.timedelta64('2', 'h')
    time_indices = [START_DATE]
    for i in range(1, num_rows):
        time_indices.append(time_indices[i-1] + np.timedelta64('1', 's'))
    return time_indices


if not os.path.exists('../data/'):
    os.makedirs('../data/')

store = get_datastore("../data/converted_sum.hdf5", 'HDF', mode='w')

"""
Gets CLEAR and MEDAL data and puts them into the store
with the right key and instance numbers.
"""
frames = get_clear_data()
for phase in range(1, 4):
    key = Key(building=1, meter=phase)
    print('Adding phase {}'.format(phase))
    store.put(str(key), frames[phase-1])


for medal_id in range(1, 16):
    frames = get_summary_data(medal_id)
    for i in range(1, 7):
        key = Key(building=1, meter=(((medal_id-1) * 6) + i + 3))
        print('Adding ' + str(key) + ' to Store')
        store.put(str(key), frames[i-1])

store.close()
convert_yaml_to_hdf5("../metadata_converter/dist", "../data/converted_sum.hdf5")
