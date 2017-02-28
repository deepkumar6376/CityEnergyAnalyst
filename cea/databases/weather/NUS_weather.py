import pandas as pd
import numpy as np
import datetime as DT
import xlrd

today = DT.datetime(2004, 5, 23)

all_data = pd.DataFrame()

for i in range(1):
    week_ago = today - DT.timedelta(days=7)
    today = week_ago

    print 'C:/Users/Bhargava/Desktop/Weather Data/' + 'W5m_' + week_ago.strftime('%Y%m%d') + '.xls'
    df = pd.read_excel('C:/Users/Bhargava/Desktop/Weather-Data/' + 'W5m_' + week_ago.strftime('%Y%m%d') + '.xlsx')
    all_data = all_data.append(df, ignore_index=True)

