from NestData import NestData
import matplotlib.pyplot as plt

# NestData useage example
twenty_twenty = NestData(2020)
sensor_df, cycles_df, events_df = twenty_twenty.get_data()

# plt.plot(events_df['date_time'], events_df['hvac_state'])
# plt.plot(events_df['heating_target'])
# plt.plot(sensor_df['avg(temp)'])
plt.show()

