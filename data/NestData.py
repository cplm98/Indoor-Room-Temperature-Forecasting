import os
import pandas as pd

class NestData():
    def __init__(self, year):
        base_dir = os.path.join("NEST", str(year))
        valid_months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        nest_files = []
        for month in valid_months:
            dir_ = os.path.join(base_dir, month)
            try:
                files = os.listdir(dir_)
                for file in files:
                    if ".csv" in file:
                        nest_files.append(os.path.join(month, file))

            except:
                print("No data for month: ", month)
                continue
        
        df_list = []
        for file in nest_files:
            df_list.append(pd.read_csv(os.path.join(base_dir, file)))

        self.df = pd.concat(df_list)
        
        self.df['Datetime'] = pd.to_datetime(self.df['Date'] + ' ' + self.df['Time']) #combine Date and Time into single DateTime index for interpolation
       
        self. df = self.df.set_index('Datetime')

        self.df = self.df.drop(columns = ['Date','Time',
            'max(nearPir)', 'min(ch1)', 'max(ch1)', 'min(ch2)', 'max(ch2)']) #drop unwanted columns

        self.df = self.df.interpolate(method='time')

    def get_data(self):
        return self.df








