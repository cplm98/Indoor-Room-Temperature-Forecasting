from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.svm import SVR
import pandas as pd
import matplotlib.pyplot as plt

# Using SVM for forecasting seems like a strange choice as they are usually best suited for binary output classification

df = pd.read_csv("../merged_data.csv")
# df.rename(columns = {'time':'Datetime'}, inplace = True) #combine Date and Time into single DateTime index for interpolation
df['time'] = pd.to_datetime(df['time'])
df.rename(columns = {'temperature':'externalTemperature', 'humidity':'externalHumidity', 'avg(temp)':'internalTemperature', 'avg(humidity)':'internalHumidity'} , inplace = True)
print(df.head(10))
df = df.set_index('time')
df = df.interpolate(method='time')
# update NA values to 0 for certain columns
df['precipAccumulation'] = df['precipAccumulation'].fillna(0)
df['precipIntensity'] = df['precipIntensity'].fillna(0)
df['nearestStormBearing'] = df['nearestStormBearing'].fillna(0)

# Line Charts
# plt.plot(df['temperature'])
# plt.plot(df['avg(temp)'])

# plt.scatter(df['avg(humidity)'], df['humidity'])
plt.show()

# print("AVG(HUMIDITY)")
# print(df['temperature'].describe())
