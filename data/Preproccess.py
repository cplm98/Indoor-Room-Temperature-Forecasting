import pandas as pd
# Basic handling of merged data file to produce data frame
df = pd.read_csv("../merged_data.csv")
df = df.set_index('time')
