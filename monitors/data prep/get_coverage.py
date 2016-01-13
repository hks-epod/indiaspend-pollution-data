import pandas as pd
import numpy as np
import datetime

input_dir = "input/"
df = pd.read_csv(input_dir+"cpcb_ambient_panel.csv")

df.dt_clean = pd.to_datetime(df.dt_clean,format='%d%b%Y %H:%M:%S')
df.date_r = pd.to_datetime(df.date_r,format='%d%b%Y')

print df

df = df[['station','parameter_name','dt_clean','date_r','monitor_read','reading_value']]
# print df

# Get minimum and maximum time for any reading
df_grouped = df.groupby('station')['dt_clean'].agg({'min_date' : np.min,'max_date' : np.max}).reset_index()
print df_grouped

dates_by_station = df_grouped.to_dict(orient='records')

df = df.loc[df.parameter_name=='PM2.5']
df = df.sort(['station','dt_clean'])
# Fill PM2.5 from that point
to_append = []
delta = datetime.timedelta(minutes=15)
for item in dates_by_station:
	station = item['station']
	print station
	min_date = item['min_date']
	max_date = item['max_date']
	print 'Max date:',max_date
	if max_date<datetime.datetime(2015,11,28):
		max_date = datetime.datetime(2015,11,28,0,0,0)
	print 'New max date:',max_date
	date = min_date
	while date<=max_date:
		print date
		if ((df['station'] == station) & (df['dt_clean'] == date)).any()==False:
			to_append.append({'station':station,'parameter_name':'PM2.5','dt_clean':date,'monitor_read':0,'date_r':datetime.datetime(date.year,date.month,date.day)})
			print 'Appended'
		date+=delta

df = df.append(to_append,ignore_index=True)
df.to_csv('output/balanced_panel.csv',index=False)

df = pd.read_csv('output/balanced_panel.csv')
df.dt_clean = pd.to_datetime(df.dt_clean)
df.date_r = pd.to_datetime(df.date_r)
print df
print df.dtypes

# get the coverage
begin_winter = datetime.datetime(2014,11,1)
begin_summer = datetime.datetime(2015,3,1)
df_winter = df.loc[(df.dt_clean>=begin_winter) & (df.dt_clean<begin_summer)]
df_since = df.loc[df.dt_clean>=begin_summer]

print df_winter.monitor_read.mean()
print df_since.monitor_read.mean()

# day
grouped = df.groupby(['station','date_r'])['monitor_read'].mean().reset_index()
print grouped
grouped.to_csv('output/daily_coverage_by_station.csv',index=False)

grouped = df.groupby(['date_r'])['monitor_read'].mean().reset_index()
print grouped
grouped.to_csv('output/daily_coverage.csv',index=False)

# month
df['month_r'] = df.date_r.apply(lambda x: datetime.datetime(x.year,x.month,1))
grouped = df.groupby(['station','month_r'])['monitor_read'].mean().reset_index()
print grouped
grouped.to_csv('output/monthly_coverage_by_station.csv',index=False)

grouped = df.groupby(['month_r'])['monitor_read'].mean().reset_index()
print grouped
grouped.to_csv('output/monthly_coverage.csv',index=False)

# week
df['week_r'] = df.date_r.apply(lambda x: x.isocalendar()[1])
df['year_r'] = df.date_r.apply(lambda x: x.isocalendar()[0])
grouped = df.groupby(['station','week_r','year_r'])['monitor_read'].mean().reset_index()
print grouped
grouped.to_csv('output/weekly_coverage_by_station.csv',index=False)

grouped = df.groupby(['week_r','year_r'])['monitor_read'].mean().reset_index()
print grouped
grouped.to_csv('output/weekly_coverage.csv',index=False)



