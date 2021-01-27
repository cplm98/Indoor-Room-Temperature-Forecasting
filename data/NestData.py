import os
import pandas as pd
import json
import sys

class NestData():
    def __init__(self, year):
        self.base_dir = os.path.join("NEST", str(year))
        valid_months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        sensor_files = [] # list of files with sensor data
        summary_files = [] # list of files with cycle summary data
        for month in valid_months:
            dir_ = os.path.join(self.base_dir, month)
            try:
                files = os.listdir(dir_)
                for file in files:
                    if ".csv" in file:
                        sensor_files.append(os.path.join(month, file))
                    if ".json" in file:
                        summary_files.append(os.path.join(month, file))

            except:
                print("No data for month: ", month)
                continue
        
        self.process_sensors(sensor_files)
        self.process_cycles(summary_files)
        self.process_events(summary_files)

    def get_data(self):
        return self.sensor_df, self.cycles_df, self.events_df

    # Events recorded in summary.json, contains target temperatures and heating cycles
    def process_events(self, file_list):
        to_df = []
        for file in file_list:
            with open(os.path.join(self.base_dir, file), 'r') as json_file:
                data = json.load(json_file)
                for day in data:
                    for event in data[day]['events']:
                        event_type = event['eventType'].split('_')[2] # eg "EVENT_TYPE_HEAT" take HEAT
                        if event_type == 'HEAT' or event_type == 'COOL': # if non-useful type, skip eg EVENT_TYPE_OFF
                            start_time = event['startTs']
                            start_time = start_time[:start_time.rfind(':')+3].replace('T', ' ')
                            duration = int(event['duration'][:-1])
                            heating_target = event['setPoint']['targets']['heatingTarget']
                            cooling_target = event['setPoint']['targets']['coolingTarget']
                            event_encoded = 0
                            if event_type == 'HEAT':
                                event_encoded = 1
                            elif event_type == 'COOL': # Looks like the cooler isn't actually hooked up
                                event_encoded = -1
                            d = {
                                'start_time' : start_time,
                                'event_encoded' : event_encoded,
                                'duration' : duration,
                                'heating_target' : heating_target,
                                'cooling_target' : cooling_target
                            }
                            to_df.append(d)
                        else:
                            continue

        df = pd.DataFrame(to_df)
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = df['start_time'] + pd.to_timedelta(df['duration'], unit='s')

        df['start_time'] = df['start_time'].round('15T') # round to 15 minute intervals
        df['end_time'] = df['end_time'].round('15T')

        # generate coninuous time range encapsulating heatin intervals
        d_range = pd.date_range(start = df['start_time'][0], end = df['end_time'].iloc[-1], freq='15T')

        heating = []
        heat_targets = []
        cool_targets = []
        i = 0 
        while i < len(d_range):
            if d_range[i] in df['start_time'].values:
                j = df['start_time'][df['start_time'] == d_range[i]].index
                heat_target = df['heating_target'].values[j][0]
                cool_target = df['cooling_target'].values[j][0]
                state_target = df['event_encoded'].values[j][0]
                while d_range[i] not in df['end_time'].values:
                    heating.append(state_target)
                    heat_targets.append(heat_target)
                    cool_targets.append(cooling_target)
                    i += 1
                heat_targets.append(heat_target)
                cool_targets.append(cooling_target)
                heating.append(state_target)
                i += 1
            else:
                heating.append(0)
                heat_targets.append(0) # Setting these to zero might not be right but we will see
                cool_targets.append(0)
                i += 1

        # Here are the names of the columns in the data frame
        events_df = pd.DataFrame({'date_time': d_range, 
                                  'hvac_state': heating,
                                  'heating_target': heat_targets,
                                  'cooling_target': cool_targets})
        events_df = events_df.set_index('date_time')
        events_df = events_df.interpolate(method='time')
        self.events_df = events_df

    # Cycles returns the heating cycles, events contains more data
    def process_cycles(self, file_list):
        to_df = []
        for file in file_list:
            with open(os.path.join(self.base_dir, file), 'r') as json_file:
                data = json.load(json_file)
                for day in data:
                    for cycle in data[day]['cycles']:
                        caption = cycle['caption']['plainText'].split(' from')[0] # just take type of cycle
                        start_time = cycle['caption']['parameters']['startTime']
                        start_time = start_time[:start_time.rfind(':')+3].replace('T', ' ') # find last colon and keep the two numbers after it
                        endTime = cycle['caption']['parameters']['endTime']
                        endTime = endTime[:endTime.rfind(':')+3].replace('T', ' ')
                        duration = cycle['duration']
                        isComplete = cycle['isComplete']
                        # Turn data into a useable coded data frame
                        if 'heating' not in caption:
                            num_caption = 0
                        else:
                            num_caption = 1
                        d = {
                            'caption' : num_caption,
                            'start_time' : start_time,
                            'endTime' : endTime,
                            'duration' : duration # we don't use this at this point
                        }
                        to_df.append(d)

        summary_df = pd.DataFrame(to_df)
        summary_df['start_time'] = pd.to_datetime(summary_df['start_time'])
        summary_df['endTime'] = pd.to_datetime(summary_df['endTime'])
        summary_df['start_time'] = summary_df['start_time'].round('15T')
        summary_df['endTime'] = summary_df['endTime'].round('15T')

        # create date range filling in all 15 minute intervals between cycle start and end time
        d_range = pd.date_range(start = summary_df['start_time'][0], end = summary_df['endTime'].iloc[-1], freq='15T')

        heating = []
        i = 0
        while i < len(d_range):
            if d_range[i] in summary_df['start_time'].values:
                while d_range[i] not in summary_df['endTime'].values:
                    heating.append(1)
                    i += 1
                heating.append(1) # basically once it finds the endTime it breaks and doesn't add for that interval, this can be removed by passing the index of the startTime that matched and using a conditional for the endTime with the same index
                i += 1
            else:
                heating.append(0)
                i += 1   
                
        # Here are the column names for the data frame
        cycles_df = pd.DataFrame({'date_time': d_range, 'hvac_state': heating})
        cycles_df = cycles_df.set_index('date_time')
        cycleds_df = cycles_df.interpolate(method='time')
        self.cycles_df = cycles_df

    def process_sensors(self, file_list):
        sensor_list = []
        for file in file_list:
            sensor_list.append(pd.read_csv(os.path.join(self.base_dir, file)))
        
        sensor_df = pd.concat(sensor_list)
        
        sensor_df['date_time'] = pd.to_datetime(sensor_df['Date'] + ' ' + sensor_df['Time']) #combine Date and Time into single DateTime index for interpolation
       
        sensor_df = sensor_df.set_index('date_time')

        sensor_df = sensor_df.drop(columns = ['Date','Time',
            'max(nearPir)', 'min(ch1)', 'max(ch1)', 'min(ch2)', 'max(ch2)']) #drop unwanted columns

        sensor_df = sensor_df.interpolate(method='time')

        self.sensor_df = sensor_df
    











