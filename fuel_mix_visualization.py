
# %%

from genericpath import exists
from sys import displayhook
import pandas as pd
import pdb
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
from sqlalchemy import create_engine
import os
from datetime import datetime
# import plotly.express as px
# import plotly.graph_objects as go
import streamlit as st

def get_clean_hist_fuel_mix(link, filename):
    # %% Download data and read into pandas dataframe
    # Arguments:    link: URL to MISO Historical Generation Fuel Mix XLSX
    #               filename: filenaming the SQLite database
    # Returns:      df: the dataframe that was written to SQLite

    df = pd.read_excel(link, engine='openpyxl', skiprows=3)

    # %% Cleaning and formatting
    df = df.dropna(axis=0, subset=['Fuel Type']) # Drop rows where Fuel Type is NaN
    df = df.dropna(axis=1, how='all') # Drop columns where header is NaN
    # df = df.loc[:, df.columns.notna()] This also worked
    df = df.drop(index=df.index[0], axis=0) # Drop the first row

    # Parsing datetime 
    df['MarketEndDatetime'] = [x + ' ' + str(y-1).zfill(2) + ':00:00.00' for x, y in zip(df['Market Date'], df["HourEnding"])]
    df['MarketEndDatetime'] = pd.to_datetime(df['MarketEndDatetime'])
    df['MarketEndDatetime'] = df['MarketEndDatetime'] + pd.Timedelta(hours=1)
    # Get rid of the original "Market Date" and "Hour Ending" columns
    df = df.drop(['Market Date', 'HourEnding'], axis=1)
    first_column = df.pop('MarketEndDatetime') 
    df.insert(0, 'MarketEndDatetime', first_column)

    # pdb.set_trace()

    # Convert Generation to Floats
    df['DA Cleared UDS Generation'] = df['DA Cleared UDS Generation'].astype('float64')
    df['[RT Generation State Estimator']=df['[RT Generation State Estimator'].astype('float64')
    df.columns = df.columns.str.replace('[^\w\s]', '', regex=True)

    # %% Export dataframe to SQLite
    engine = create_engine(f'sqlite:///{filename}', echo=True)
    df.to_sql('Historical Fuel Generation Mix', con=engine, if_exists='replace')

    # pdb.set_trace()

    return df

if __name__ = '__main__':

    # %% Find SQLite DB or get fresh data
    link = "https://docs.misoenergy.org/marketreports/historical_gen_fuel_mix_2021.xlsx"
    # Above link can be found here: 
    # https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/#nt=%2FMarketReportType%3ASummary%2FMarketReportName%3AHistorical%20Generation%20Fuel%20Mix%20(xlsx)&t=10&p=0&s=MarketReportPublished&sd=desc
    db_name = "historical_fuel_mix.sqlite"

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Check if the database file exists.  If not, re-download a fresh one from the link.
    if not os.path.exists(db_name):
        print("Database file not found.  Importing fresh data.")
        df = get_clean_hist_fuel_mix(link, db_name)


    # %% Load the SQLite Database
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    df = pd.read_sql("""select * from "Historical Fuel Generation Mix";""", conn, parse_dates=[ \
        "Market Date"])


    # %% Plot production of first day over the hour (for now)

    # date = '2021-05-01'
    # regions=["North", "South", "Central"]
    # df_day = pd.read_sql(f"""SELECT * FROM "Historical Fuel Generation Mix"
    #                         WHERE DATE(MarketEndDatetime)='{date}'
    #                         AND "Region" IN {tuple(regions)};""", conn)

    fuel_types = df["Fuel Type"].unique()
    display_vec_dict = {}
    # display_vec_dict["Time"] = [datetime.fromisoformat(x) for x in df_day["MarketEndDatetime"].unique()]

    # for fuel in fuel_types:
    #     display_vec_dict[fuel] = df_day.query(f'`Fuel Type`=="{fuel}"').groupby('MarketEndDatetime').sum()["DA Cleared UDS Generation"].to_numpy()

    fig = plt.figure()
    ax = plt.subplot(111)

    # px = 1/plt.rcParams['figure.dpi']
    # fig, ax = plt.subplots(figsize=(400*px, 300*px))

    # ax.stackplot(display_vec_dict['Time'], \
    #         display_vec_dict['Coal'],\
    #         display_vec_dict['Gas'],\
    #         display_vec_dict['Wind'],\
    #         display_vec_dict['Nuclear'],\
    #         display_vec_dict['Hydro'],\
    #         display_vec_dict['Solar'],\
    #         display_vec_dict['Other'], labels=fuel_types)

    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # %% Streamlit
    st.set_page_config(page_title="MISO Historical Fuel Mix Visualization", page_icon=":bar_chart:", layout="wide")

    # Streamlit Sidebar
    st.sidebar.title('MISO Historical Fuel Mix Visualization')

    st.sidebar.header('Select Filters Here:')

    regions = st.sidebar.multiselect(
        "Select regions to include",
        options=df["Region"].unique(), 
        # default='Central'
        default=df["Region"].unique()
    )

    default_date = datetime.fromisoformat('2021-01-01')
    min_date = datetime.fromisoformat(df['MarketEndDatetime'].min())
    max_date = datetime.fromisoformat(df['MarketEndDatetime'].max())

    select_day = st.sidebar.date_input(
        "Select date", value=default_date, min_value=min_date, max_value=max_date)

    # binning = st.sidebar.selectbox(
    #     "Select binning (under construction, doesn't work)",
    #     options=["Day", "Week", "Month"]
    # )

    st.sidebar.header('Description')
    st.sidebar.markdown('''In this app, you can explore the hourly generation fuel mix for 
                        any MISO region on any day in 2021.  I will be adding data from more 
                        years as well as gradually adding more functionality, including the 
                        ability to aggregate the data in larger temporal bins, so you can 
                        see the fuel mix change over weeks and months.''')
    st.sidebar.markdown('''For more information, see this project's [Github repo page](https://github.com/kpwang66/MISO-Historical-Fuel-Mix-Visualization).
    ''')

    # %%

    date = select_day.strftime("%Y-%m-%d")
    SQL_query = f"""SELECT * FROM "Historical Fuel Generation Mix"
                            WHERE DATE(MarketEndDatetime)='{date}'
                            AND "Region" IN {tuple(regions)};"""
    SQL_query = SQL_query.replace(',)', ')')
    df_day = pd.read_sql(SQL_query, conn)

    display_vec_dict["Datetime"] = [datetime.fromisoformat(x) for x in df_day["MarketEndDatetime"].unique()]

    display_vec_dict["Time"] = np.array([str(x.time()) for x in display_vec_dict["Datetime"]])

    for fuel in fuel_types:
        display_vec_dict[fuel] = df_day.query(f'`Fuel Type`=="{fuel}"').groupby('MarketEndDatetime').sum()["DA Cleared UDS Generation"].to_numpy()

        if len(display_vec_dict[fuel]) == 0:
            display_vec_dict[fuel] = np.zeros((1, 23))

    # %% 

    ax.stackplot(display_vec_dict['Time'], \
            display_vec_dict['Coal'],\
            display_vec_dict['Gas'],\
            display_vec_dict['Wind'],\
            display_vec_dict['Nuclear'],\
            display_vec_dict['Hydro'],\
            display_vec_dict['Solar'],\
            display_vec_dict['Other'], labels=fuel_types)

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax.set_title('MISO Historical Fuel Mix: ' + date)
    ax.set_ylabel('DA Cleared UDS Generation [MW]')
    ax.set_xlabel('Hour Ending')
    plt.xticks(rotation = 45)

    # Replace xtick datetimes to ints for hour of day
    xtick_labels = list(range(1, 24, 2))
    plt.xticks(xtick_labels)

    plt.show()
    st.pyplot(fig)

    # pdb.set_trace()
    # %%
