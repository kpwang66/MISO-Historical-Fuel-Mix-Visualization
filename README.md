# MISO Historical Generation Fuel Mix Visualization

## Use

The deployed app is hosted via Streamlit Community (thank you :pray:) and [is available here](https://kpwang66-miso-historical-fuel-mix-fuel-mix-visualization-a40nki.streamlitapp.com/).

## Local Development

For working with this app locally, first install the dependencies with pip (Python 3.7+):

```shell
$ pip install -r requirements.txt
``` 

To launch the Streamlit app locally, simply run:

```shell
$ streamlit run fuel_mix_visualization.py
```

View the app in your browser on [http://localhost:8501/](http://localhost:8501/).

## Motivation
This is a small app that I'm developing to help teach myself some contemporary tools of data analytics and data science while continuing to explore the field of energy systems.  While I have used Python for years as a graduate researcher, mostly the codes I developed were a "one-off" needed to provide a particular research function or solve a particular problem.  In developing this app, I'm trying to cover the following topics:
- Fetching data and cleaning data with pandas
- Creating an SQL database
- Expanding and joining SQL databases
- Querying data from an SQL database and passing to pandas to process
- Developing a user-friendly interface to explore the data with Streamlit
- Version control and documenting a project with Git and Github

## Background

MISO (Midcontinent Independent System Operator) is the non-profit entity that coordinates and monitors the electric power system and manages the electricity market in a region including Manitoba, Canada, much of the American Midwest, and a southern section including Arkansas, Mississippi, and Louisiana:

![Map of MISO's reliability regions: North (blue), Central (green), and South (orange)](./miso-map.png)

In this app, you can explore the hourly generation fuel mix for any MISO region on any day in 2021.  I will be adding data from more years as well as gradually adding more functionality, including the ability to aggregate the data in larger temporal bins, so you can see the fuel mix change over weeks and months.

The data files are available from MISO's website in the form of XLSX files [here](https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/#nt=%2FMarketReportType%3ASummary%2FMarketReportName%3AHistorical%20Generation%20Fuel%20Mix%20(xlsx)&t=10&p=0&s=MarketReportPublished&sd=desc).  Alternatively, you can navigate to this part of their [website](https://www.misoenergy.org) by going to Markets and Operations > Real-Time and Market Data > Market Reports > Summary > Historical Generation Fuel Mix (xlsx).

### Known Issues
- Occassionally there are missing hourly entries in the MISO data for a particular region and fuel type, which will cause an error.  I will need to figure out a way to detect these gaps in the data and fill in 0 generation for when this occurs.
