import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

EUR_DATA_URL = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/json'


def add_missing_dates_eur(df_eur_new):
    """
    Adds the missing dates from the first day of data recorded until today
    :param df_eur_new: cleaned and formatted europe data
    :return: preprocessed eur data
    """
    all_days = pd.date_range(df_eur_new['REPORT_DATE'].min(), df_eur_new['REPORT_DATE'].max(), freq='D')
    countries = df_eur_new['COUNTRY_ALPHA_3_CODE'].unique()
    temp = df_eur_new
    min__ = all_days.min()
    max_ = all_days.max()
    for country in countries:
        # print(country)
        tab = df_eur_new[(df_eur_new['COUNTRY_ALPHA_3_CODE'] == country)]
        tab = tab.reset_index(drop=True)
        data = pd.DataFrame(tab.iloc[0])
        count = 0
        for day in all_days:
            if day not in tab['REPORT_DATE'].values:
                count += 1
                if day == min__:
                    data.loc['PEOPLE_POSITIVE_CASES_COUNT'] = 0
                    data.loc['PEOPLE_DEATH_COUNT'] = 0
                else:
                    prev_date_data = temp[
                        (temp['COUNTRY_ALPHA_3_CODE'] == country) & (temp['REPORT_DATE'] == (day - timedelta(1)))]
                    prev_date_data = prev_date_data.reset_index(drop=True)
                    data = pd.DataFrame(prev_date_data.iloc[0])
                data.loc['PEOPLE_POSITIVE_NEW_CASES_COUNT'] = 0
                data.loc['PEOPLE_DEATH_NEW_COUNT'] = 0
                data.loc['REPORT_DATE'] = day
                temp = temp.append([data[0]])
        # break
        print(f"handling missing dates in : country-{country} added-{count}")
    df_eur_new = temp
    df_eur_new = df_eur_new.reset_index(drop=True)
    df_eur_new = df_eur_new.sort_values(['COUNTRY_ALPHA_3_CODE', 'REPORT_DATE'])
    df_eur_new
    return df_eur_new


def clean_europe():
    """
    Reads the raw europe data and formats to a standard format
    :return: properly cleaned, added missing values europe data
    """
    print("Cleaning europe source...")
    resp = requests.get(EUR_DATA_URL)
    data = resp.json()
    # with open('data.txt', 'w') as outfile:
    #     json.dump(data, outfile)
    # with open('data.txt') as json_file:
    #     data = json.load(json_file)
    df_europe = pd.DataFrame(data['records'])
    df_europe = df_europe[df_europe['countryterritoryCode'] != 'USA']
    df_europe = df_europe[df_europe['countryterritoryCode'] != 'CAN']
    df_eur_new = pd.DataFrame(
        df_europe[['continentExp', 'countriesAndTerritories', 'countryterritoryCode', 'dateRep', 'cases', 'deaths']])
    df_eur_new['dateRep'] = df_eur_new['dateRep'].apply(lambda a: datetime.strptime(a, '%d/%m/%Y'))
    # df_eur_new['dateRep'] = pd.to_datetime(df_eur_new['dateRep'])
    df_eur_new = df_eur_new.sort_values(['countryterritoryCode', 'dateRep'])
    df_eur_new = df_eur_new.reset_index(drop=True)
    df_eur_new = df_eur_new[df_eur_new['countryterritoryCode'].notnull()]
    df_eur_new['cases_cum'] = 0
    df_eur_new['deaths_cum'] = 0
    df_eur_grouped = df_eur_new.groupby('countryterritoryCode')
    ct_i = df_eur_new.columns.get_loc('cases')
    c_i = df_eur_new.columns.get_loc('cases_cum')
    dt_i = df_eur_new.columns.get_loc('deaths')
    d_i = df_eur_new.columns.get_loc('deaths_cum')
    c = 0
    for group_name, df_group in df_eur_grouped:
        df_eur_new.iat[c, c_i] = df_group.iat[0, ct_i]
        df_eur_new.iat[c, d_i] = df_group.iat[0, dt_i]
        c += 1
        for row in range(1, len(df_group)):
            val_c = df_group.iat[row, ct_i] + df_eur_new.iat[c - 1, c_i]
            if val_c >= 0:
                df_eur_new.iat[c, c_i] = val_c
            val_d = df_group.iat[row, dt_i] + df_eur_new.iat[c - 1, d_i]
            if val_d >= 0:
                df_eur_new.iat[c, d_i] = val_d
            c += 1
    df_eur_new = df_eur_new.rename(
        columns={'continentExp': 'CONTINENT_NAME', 'dateRep': 'REPORT_DATE', 'cases_cum': 'PEOPLE_POSITIVE_CASES_COUNT',
                 'cases': 'PEOPLE_POSITIVE_NEW_CASES_COUNT',
                 'deaths_cum': 'PEOPLE_DEATH_COUNT', 'deaths': 'PEOPLE_DEATH_NEW_COUNT',
                 'countriesAndTerritories': 'COUNTRY_SHORT_NAME', 'countryterritoryCode': 'COUNTRY_ALPHA_3_CODE'})
    df_eur_new['DATA_SOURCE_NAME'] = 'European Centre for Disease Prevention and Control'
    df_eur_new = df_eur_new.reset_index(drop=True)
    return add_missing_dates_eur(df_eur_new)


def add_missing_dates_usa(df_usa_new):
    """
    Adds the missing dates from the first day of data recorded until today
    :param df_usa_new: cleaned and formatted usa data
    :return: preprocessed usa data
    """
    all_days = pd.date_range(df_usa_new['REPORT_DATE'].min(), df_usa_new['REPORT_DATE'].max(), freq='D')
    states = df_usa_new['PROVINCE_STATE_NAME'].unique()
    temp = df_usa_new
    min_ = pd.to_datetime(df_usa_new['REPORT_DATE'].min())
    max_ = df_usa_new['REPORT_DATE'].max()
    for state in states:
        print(f"state {state}")
        counties = df_usa_new[(df_usa_new['PROVINCE_STATE_NAME'] == state)]['COUNTY_NAME'].unique()
        for county in counties:
            tab = df_usa_new[(df_usa_new['PROVINCE_STATE_NAME'] == state) & (df_usa_new['COUNTY_NAME'] == county)]
            tab = tab.reset_index(drop=True)
            data = pd.DataFrame(tab.iloc[0])
            my_list = []
            for day in all_days:
                da = day.strftime('%Y-%m-%d')
                if da not in tab['REPORT_DATE'].values:
                    my_list.append(day)
            newdf = pd.DataFrame(np.repeat(data.T.values, len(my_list), axis=0))
            newdf.columns = data.T.columns
            for i, day in enumerate(my_list):
                da = day.strftime('%Y-%m-%d')
                if day == min_:
                    newdf.loc[i, 'PEOPLE_POSITIVE_CASES_COUNT'] = 0
                    newdf.loc[i, 'PEOPLE_DEATH_COUNT'] = 0
                else:
                    p_date = (day - timedelta(1))
                    if p_date in my_list:
                        prev_date_data = newdf[newdf['REPORT_DATE'] == p_date.strftime('%Y-%m-%d')]
                    else:
                        prev_date_data = tab[tab['REPORT_DATE'] == p_date.strftime('%Y-%m-%d')]
                    newdf.loc[i, 'PEOPLE_POSITIVE_CASES_COUNT'] = prev_date_data['PEOPLE_POSITIVE_CASES_COUNT'].values[
                        0]
                    newdf.loc[i, 'PEOPLE_DEATH_COUNT'] = prev_date_data['PEOPLE_DEATH_COUNT'].values[0]
                newdf.loc[i, 'PEOPLE_POSITIVE_NEW_CASES_COUNT'] = 0
                newdf.loc[i, 'PEOPLE_DEATH_NEW_COUNT'] = 0
                newdf.loc[i, 'REPORT_DATE'] = da
            temp = pd.concat([temp, newdf])
            print(f"handling missing dates in : state-{state} county-{county} added-{len(my_list)}")
    df_usa_new = temp
    df_usa_new = df_usa_new.reset_index(drop=True)
    df_usa_new = df_usa_new.sort_values(['PROVINCE_STATE_NAME', 'COUNTY_NAME', 'REPORT_DATE'])
    return df_usa_new


def clean_usa():
    """
    Reads the raw usa data and formats to a standard format
    :return: properly cleaned, added missing values usa data
    """
    print("Cleaning usa source...")
    dfUsa = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
    # dfUsa = pd.read_csv('test_usa.csv')
    # dfUsa.to_csv('test_usa.csv',index=False)
    df_usa_new = pd.DataFrame(dfUsa)
    df_usa_new = df_usa_new.sort_values(['state', 'county', 'date'])
    df_usa_new = df_usa_new.reset_index(drop=True)
    df_usa_new['cases_today'] = 0
    df_usa_new['deaths_today'] = 0
    df_outer_grp = df_usa_new.groupby('state')
    ct_i = df_usa_new.columns.get_loc('cases_today')
    c_i = df_usa_new.columns.get_loc('cases')
    dt_i = df_usa_new.columns.get_loc('deaths_today')
    d_i = df_usa_new.columns.get_loc('deaths')
    c = 0
    for gn, df_inner_grp in df_outer_grp:
        df1_grouped = df_inner_grp.groupby('county')
        for group_name, df_group in df1_grouped:
            df_usa_new.iat[c, ct_i] = df_group.iat[0, c_i]
            df_usa_new.iat[c, dt_i] = df_group.iat[0, d_i]
            c += 1
            for row in range(1, len(df_group)):
                val_c = df_group.iat[row, c_i] - df_group.iat[row - 1, c_i]
                if val_c >= 0:
                    df_usa_new.iat[c, ct_i] = val_c
                val_d = df_group.iat[row, d_i] - df_group.iat[row - 1, d_i]
                if val_d >= 0:
                    df_usa_new.iat[c, dt_i] = val_d
                c += 1
    df_usa_new = df_usa_new.rename(
        columns={'state': 'PROVINCE_STATE_NAME', 'county': 'COUNTY_NAME', 'date': 'REPORT_DATE',
                 'fips': 'COUNTY_FIPS_NUMBER', 'cases': 'PEOPLE_POSITIVE_CASES_COUNT',
                 'cases_today': 'PEOPLE_POSITIVE_NEW_CASES_COUNT',
                 'deaths': 'PEOPLE_DEATH_COUNT', 'deaths_today': 'PEOPLE_DEATH_NEW_COUNT'})
    df_usa_new['COUNTRY_ALPHA_3_CODE'] = 'USA'
    df_usa_new['COUNTRY_SHORT_NAME'] = 'United States'
    df_usa_new['DATA_SOURCE_NAME'] = 'New York Times'
    df_usa_new['CONTINENT_NAME'] = 'America'
    df_usa_new = df_usa_new.reset_index(drop=True)
    return add_missing_dates_usa(df_usa_new)


def add_missing_dates_can(df_usa_new, df_can_new):
    """
    Adds the missing dates from the first day of data recorded until today in the America continent
    :param df_usa_new: cleaned and formatted usa data
    :param df_can_new: cleaned and formatted canada data
    :return: preprocessed canada data
    """
    all_days = pd.date_range(df_usa_new['REPORT_DATE'].min(), df_usa_new['REPORT_DATE'].max(), freq='D')
    states = df_can_new['PROVINCE_STATE_NAME'].unique()
    temp = df_can_new
    min__ = all_days.min()
    max_ = all_days.max()
    for state in states:
        # print(state)
        tab = df_can_new[(df_can_new['PROVINCE_STATE_NAME'] == state)]
        tab = tab.reset_index(drop=True)
        data = pd.DataFrame(tab.iloc[0])
        count = 0
        for day in all_days:
            if day not in tab['REPORT_DATE'].values:
                count += 1
                if day == min__:
                    data.loc['PEOPLE_POSITIVE_CASES_COUNT'] = 0
                    data.loc['PEOPLE_DEATH_COUNT'] = 0
                else:
                    prev_date_data = temp[
                        (temp['PROVINCE_STATE_NAME'] == state) & (temp['REPORT_DATE'] == (day - timedelta(1)))]
                    prev_date_data = prev_date_data.reset_index(drop=True)
                    data = pd.DataFrame(prev_date_data.iloc[0])
                data.loc['PEOPLE_POSITIVE_NEW_CASES_COUNT'] = 0
                data.loc['PEOPLE_DEATH_NEW_COUNT'] = 0
                data.loc['REPORT_DATE'] = day
                temp = temp.append([data[0]])
        print(f"handling missing dates in : state-{state} added-{count}")
    df_can_new = temp
    df_can_new = df_can_new.reset_index(drop=True)
    df_can_new = df_can_new.sort_values(['PROVINCE_STATE_NAME', 'REPORT_DATE'])
    df_can_new
    return df_can_new


def clean_canada(df_usa_new):
    """
    Reads the raw canada data and formats to a standard format
    :param df_usa_new: cleaned usa data
    :return: properly cleaned, added missing values canada data
    """
    print("Cleaning canada source...")
    # dfCanada = pd.read_csv("canada_11_18.csv")
    csv_url = 'https://health-infobase.canada.ca/src/data/covidLive/covid19-download.csv'
    req = requests.get(csv_url)
    url_content = req.content
    csv_file = open('canada_download.csv', 'wb')
    csv_file.write(url_content)
    csv_file.close()
    dfCanada = pd.DataFrame(pd.read_csv('canada_download.csv'))
    df_can_new = pd.DataFrame(dfCanada[['prname', 'date', 'numconf', 'numtoday', 'numdeaths', 'numdeathstoday']])
    df_can_new['date'] = df_can_new['date'].apply(lambda a: datetime.strptime(a, '%Y-%m-%d'))
    # df_can_new['date']=pd.to_datetime(df_can_new['date'])
    df_can_new = df_can_new.sort_values(by=['prname', 'date'])
    df_can_new = df_can_new.rename(
        columns={'prname': 'PROVINCE_STATE_NAME', 'date': 'REPORT_DATE', 'numconf': 'PEOPLE_POSITIVE_CASES_COUNT',
                 'numtoday': 'PEOPLE_POSITIVE_NEW_CASES_COUNT',
                 'numdeaths': 'PEOPLE_DEATH_COUNT', 'numdeathstoday': 'PEOPLE_DEATH_NEW_COUNT'})
    df_can_new['COUNTRY_ALPHA_3_CODE'] = 'CAN'
    df_can_new['COUNTRY_SHORT_NAME'] = 'Canada'
    df_can_new['DATA_SOURCE_NAME'] = 'Public Health Agency of Canada'
    df_can_new['CONTINENT_NAME'] = 'America'
    df_can_new = df_can_new[df_can_new['PROVINCE_STATE_NAME'] != 'Canada']
    df_can_new = df_can_new.reset_index(drop=True)
    return add_missing_dates_can(df_usa_new, df_can_new)
