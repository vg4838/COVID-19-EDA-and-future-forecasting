import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', 5000)
pd.set_option('display.max_rows', 5000)
import statsmodels.api as sm

def arima(file):
    print("ARIMA processing")
    df = pd.read_excel(file)
    country_dict = dict(df["COUNTRY_SHORT_NAME"])
    df['Date'] = pd.to_datetime(df.REPORT_DATE)
    df.sort_values(by='Date',inplace=True)
    ftr = (df['REPORT_DATE'] + pd.Timedelta(16, unit='W')).to_frame()
    ftr['CONTINENT_NAME'] = None
    ftr['COUNTRY_SHORT_NAME'] = None
    ftr['COUNTRY_ALPHA_3_CODE'] =None
    ftr['PEOPLE_POSITIVE_NEW_CASES_COUNT'] = 0
    ftr['PEOPLE_DEATH_NEW_COUNT'] = 0
    ftr['PEOPLE_POSITIVE_CASES_COUNT'] = 0
    ftr['PEOPLE_DEATH_COUNT'] = 0
    ftr["DATA_SOURCE_NAME"] = None
    ftr["COUNTY_NAME"] = None
    ftr["PROVINCE_STATE_NAME"] = None
    ftr["COUNTY_FIPS_NUMBER"] = None

    df1 = pd.concat([df, ftr], ignore_index=True)
    df1.sort_values(by='Date',inplace=True)
    X_train = df[:int(len(df)*0.90)]
    df1.TimeStamp = pd.to_datetime(df1["REPORT_DATE"],format='%d-%m-%Y %H:%M')
    df1.index = df1.TimeStamp
    df1 = df1.resample('D').mean()
    X_train.TimeStamp = pd.to_datetime(X_train["REPORT_DATE"],format='%d-%m-%Y %H:%M')
    X_train.index = X_train.TimeStamp
    X_train = X_train.resample('D').mean()

    y_avg = df1.copy()
    fit1 = sm.tsa.statespace.SARIMAX(X_train.PEOPLE_POSITIVE_CASES_COUNT, order=(2, 1, 4),seasonal_order=(0,1,1,7)).fit()
    y_avg['SARIMA'] = fit1.predict(start="2020-08-06", end="2021-1-06", dynamic=True)
    plt.figure(figsize=(16,8))
    plt.plot( X_train['PEOPLE_POSITIVE_CASES_COUNT'], label='Actual')
    plt.plot(y_avg['SARIMA'] , label='Prediction')
    plt.ylabel("AVG. People Positive Cases Count")
    plt.legend(loc='best')
    plt.savefig("Actual and Prediction using ARIMA.png")
    plt.show()

