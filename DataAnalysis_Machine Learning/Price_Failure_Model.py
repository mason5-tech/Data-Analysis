#!/usr/bin/env python
# coding: utf-8

# In[39]:


# !/usr/bin/python
# -*- coding: utf-8 -*-

# plot feature importance using built-in function


import sys
import os
sys.path.append(os.path.abspath(r"C:\Users\Mma4\Desktop\FailuresReport"))

from Toolbox import time_value
from numpy import loadtxt
from xgboost import XGBClassifier
from xgboost import plot_importance
from matplotlib import pyplot
import pandas as pd
import xgboost as xgb
import joblib


# load data
# CountryId=  pd.read_csv(r'C:\Users\Mma4\Desktop\FailuresReport\performanceId and CountryId.csv')

@time_value
def Pre_Failure(**kwargs):
    kwargs['dataset_Out_Scope'].FailureTaskGeneratedTime = pd.to_datetime(
        kwargs['dataset_Out_Scope'].FailureTaskGeneratedTime)
    # dataset = dataset.set_index('FailureTaskGeneratedTime')

    kwargs['CountryId'].columns = ['InvestmentId', 'Country']

    header_string = 'FileId,DeliveryId,InvestmentId,DataUnit,ZoneId,ValidationCodeId,ActionType,ActionUserID,DeliveryId,FailureTaskGeneratedTime,TaskDoneTime,Taskowner,TaskownerUserName,FileUserID,ProcessTime,FailureType,workday'
    header_list = header_string.split(sep=',')
    try:
        kwargs['dataset_Scope'].columns = header_list
    except:
        pass
    kwargs['dataset_Scope'].FailureTaskGeneratedTime = pd.to_datetime(kwargs['dataset_Scope'].FailureTaskGeneratedTime)

    dataset = kwargs['dataset_Scope']

    dataset = pd.merge(dataset, kwargs['CountryId'], on='InvestmentId')

    dataset_country = dataset.groupby('Country').count()
    dataset_country = pd.DataFrame(dataset_country['InvestmentId'])

    dataset_country_list = dataset_country.index.to_list()

    Total = len(dataset)

    list_EMEA = ['ALB', 'AND', 'AUT', 'BLR', 'BEL', 'BGR', 'CAF', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FRO', 'FIN',
                 'FRA',
                 'MKD', 'MLT', 'MDA', 'DEU', 'GIB', 'GRC', 'GRL', 'GGY', 'HUN', 'ISL', 'IRL', 'IMN', 'ITA', 'JEY',
                 'LVA', 'LIE', 'LTU', 'LUX',
                 'MCO', 'MNE', 'NLD', 'NOR', 'POL', 'PRT', 'ROU', 'RUS', 'SMR', 'SX', 'SVK', 'SVN', 'SGS', 'ESP', 'SWE',
                 'CHE', 'TUR', 'UKR', 'UK', 'GBR']

    list_AUS = ['AUS', 'NZ', 'NZL']
    List_US = ['US', 'USA']

    dataset_country_list = ['EMEA' if x in list_EMEA else x for x in dataset_country_list]
    dataset_country_list = ['AUS' if x in list_AUS else x for x in dataset_country_list]
    dataset_country_list = ['US' if x in List_US else x for x in dataset_country_list]

    dataset_country_Big = dataset_country.reset_index()
    dataset_country_Big.Country = dataset_country_list
    dataset_country_Big.columns = ['Country', 'InvestmentId']
    dataset_country_Big = dataset_country_Big.groupby('Country').sum()

    dataset_country_Big_ratio = pd.DataFrame(dataset_country_Big.InvestmentId / Total)
    # dataset_country_Big_ratio.sort_values('InvestmentId', ascending=False).head(7)

    EMEA_number = dataset_country_Big_ratio.loc['EMEA']
    US_number = dataset_country_Big_ratio.loc['US']
    AUS_number = dataset_country_Big_ratio.loc['AUS']
    CAN_number = dataset_country_Big_ratio.loc['CAN']
    KOR_number = dataset_country_Big_ratio.loc['KOR']
    IND_number = dataset_country_Big_ratio.loc['IND']
    BRA_number = dataset_country_Big_ratio.loc['BRA']

    dataset_country['Country Weight'] = dataset_country.InvestmentId / Total
    dataset_country = dataset_country.sort_values('Country Weight', ascending=False)
    dataset_country = dataset_country.reset_index(drop=False)
    dataset_country = dataset_country[['Country', 'Country Weight']]

    dataset_updated = pd.merge(dataset, dataset_country, on='Country')

    result_Weight = dataset_updated.groupby('FailureTaskGeneratedTime')['Country Weight'].sum()

    result_Weight = result_Weight.resample('D').sum()

    result_Weight = pd.DataFrame(result_Weight)
    result_Weight = result_Weight.reset_index()

    result_Sum = dataset.groupby('FailureTaskGeneratedTime').InvestmentId.count().fillna(0)

    result_Sum = result_Sum.resample('D').sum()

    result_Sum = pd.DataFrame(result_Sum)
    result_Sum['Total'] = result_Sum.apply(lambda x: x.sum(), axis=1)

    result_Sum = result_Sum.iloc[:, -1:]
    # result_Sum
    result_Sum = result_Sum.reset_index()

    result_Sum = pd.merge(result_Sum, result_Weight, on='FailureTaskGeneratedTime').set_index(
        'FailureTaskGeneratedTime')

    result_Sum_2018 = result_Sum[result_Sum.index > '2020-01-01']
    result_Sum_2018shift = result_Sum[result_Sum.index > '2019-12-31']
    result_Sum_2018['Weekdays'] = result_Sum_2018.index.to_series().dt.dayofweek
    result_Sum_weekdays = result_Sum_2018[result_Sum_2018.Weekdays != 6]  # 不要周日
    result_Sum_weekdays = result_Sum_weekdays[result_Sum_2018.Weekdays != 5]  # 不要周6
    # 把周末的值加到周一去
    result_Sat_Sun = result_Sum_2018[result_Sum_2018.Weekdays == 5].Total.values + result_Sum_2018[
        result_Sum_2018.Weekdays == 6].Total.values
    if len(result_Sum_weekdays[result_Sum_weekdays.Weekdays == 0].Total) == len(result_Sat_Sun):
        new_Monday = result_Sum_weekdays[result_Sum_weekdays.Weekdays == 0].Total + result_Sat_Sun
    if len(result_Sum_weekdays[result_Sum_weekdays.Weekdays == 0].Total) < len(result_Sat_Sun):
        new_Monday = result_Sum_weekdays[result_Sum_weekdays.Weekdays == 0].Total + result_Sat_Sun[:-1]

    # result_Sum_weekdays[result_Sum_weekdays.Weekdays==0].Total = new_Monday
    New_result_Sum_weekdays = result_Sum_weekdays.replace(
        result_Sum_weekdays[result_Sum_weekdays.Weekdays == 0].Total.values, new_Monday.values)
    New_result_Sum_weekdays.Weekdays = New_result_Sum_weekdays.Weekdays + 1
    Month = New_result_Sum_weekdays.reset_index().FailureTaskGeneratedTime.apply(lambda x: x.strftime("%m"))
    Day = New_result_Sum_weekdays.reset_index().FailureTaskGeneratedTime.apply(lambda x: x.strftime("%d"))
    New_result_Sum_weekdays['Month'] = Month.values
    New_result_Sum_weekdays['Day'] = Day.values

    New_result_Sum_weekdays.head()
    shift = pd.DataFrame(result_Sum_2018shift.Total.shift(periods=1))
    shift.columns = ['T-1']

    New_result_Sum_weekdays = pd.merge(New_result_Sum_weekdays.reset_index(), shift.reset_index(), how='left',
                                       on='FailureTaskGeneratedTime')
    New_result_Sum_weekdays = New_result_Sum_weekdays.set_index('FailureTaskGeneratedTime')

    kwargs['Holiday'].Date = pd.to_datetime(kwargs['Holiday'].Date)

    grouper_Holiday = kwargs['Holiday'].groupby([pd.Grouper('Date'), 'Region'])  # pd.Grouper('EffectiveDate'),

    result_Holiday = grouper_Holiday['Date'].count().unstack(['Region']).fillna(0)
    # print(result_Holiday.columns)
    # result_Holiday = result_Holiday[['US','EMEA','Canada','Australasia']]

    # Holiday_2019_list = list(set(Holiday.Date.to_list()))#unqiue()
    # Holiday_list = New_result_Sum_weekdays_updated.index
    # grouper_Holiday_Countries= Holiday.groupby([pd.Grouper('Date'), 'Domicile']) #pd.Grouper('EffectiveDate'),

    # result_Holiday_Countries = grouper_Holiday_Countries['Date'].count().unstack(['Domicile']).fillna(0)
    # result_Holiday_Countries
    Domicile = kwargs['Holiday'].Domicile.to_list()
    list_AUS_full = ['New Zealand', 'Australia']
    list_EMEA_full = ['Andorra',
                      'Austria',
                      'Bahrain',
                      'Belgium',
                      'Botswana',
                      'Croatia',
                      'Cyprus',
                      'Czech Republic',
                      'Denmark',
                      'Egypt',
                      'Estonia',
                      'Finland',
                      'France',
                      'Germany',
                      'Gibraltar',
                      'Greece',
                      'Guernsey',
                      'Hungary',
                      'Iceland',
                      'Ireland',
                      'Isle of Man',
                      'Israel',
                      'Italy',
                      'Jersey',
                      'Jordan',
                      'Kenya',
                      'Kuwait',
                      'Latvia',
                      'Lebanon',
                      'Lesotho',
                      'Liechtenstein',
                      'Lithuania',
                      'Luxembourg',
                      'Malta',
                      'Mauritius',
                      'Mayotte',
                      'Monaco',
                      'Morocco',
                      'Namibia',
                      'Netherlands',
                      'Norway',
                      'Oman',
                      'Poland',
                      'Portugal',
                      'Qatar',
                      'Romania',
                      'Russia',
                      'Saint Vincent and the Gre',
                      'San Marino',
                      'Saudi Arabia',
                      'Slovakia',
                      'Slovenia',
                      'South Africa',
                      'Spain',
                      'Swaziland',
                      'Sweden',
                      'Switzerland',
                      'Tunisia',
                      'Turkey',
                      'United Arab Emirates',
                      'United Kingdom',
                      'United States Virgin Isla']

    Domicile = ['EMEA' if x in list_EMEA_full else x for x in Domicile]
    Domicile = ['AUS' if x in list_AUS_full else x for x in Domicile]
    Domicile = ['US' if x == 'United States' else x for x in Domicile]
    Domicile = ['IND' if x == 'India' else x for x in Domicile]
    Domicile = ['KOR' if x == 'South Korea' else x for x in Domicile]
    Domicile = ['BRA' if x == 'Brazil' else x for x in Domicile]

    kwargs['Holiday'].Domicile = Domicile

    grouper_Domicile = kwargs['Holiday'].groupby([pd.Grouper('Date'), 'Domicile'])  # pd.Grouper('EffectiveDate'),

    result_Domicile = grouper_Domicile['Date'].count().unstack(['Domicile']).fillna(0)
    result_Domicile = result_Domicile[['EMEA', 'US', 'AUS', 'Canada', 'BRA', 'KOR', 'IND']]
    result_Domicile.loc['Total'] = result_Domicile.apply(lambda x: x.sum(), axis=0)
    result_Domicile['EMEA'] = result_Domicile['EMEA'] / result_Domicile.loc['Total'].EMEA
    result_Domicile['US'] = result_Domicile['US'] / result_Domicile.loc['Total'].US
    result_Domicile['AUS'] = result_Domicile['AUS'] / result_Domicile.loc['Total'].AUS
    result_Domicile['Canada'] = result_Domicile['Canada'] / result_Domicile.loc['Total'].Canada
    result_Domicile['BRA'] = result_Domicile['BRA'] / result_Domicile.loc['Total'].BRA
    result_Domicile['KOR'] = result_Domicile['KOR'] / result_Domicile.loc['Total'].KOR
    result_Domicile['IND'] = result_Domicile['IND'] / result_Domicile.loc['Total'].IND
    result_Domicile = result_Domicile.iloc[:-1, :]

    New_result_Sum_weekdays_without_index = New_result_Sum_weekdays.reset_index()
    # New_result_Sum_weekdays_without_index = New_result_Sum_weekdays_without_index[New_result_Sum_weekdays_without_index.index > '2018-12-31']
    New_result_Sum_weekdays_without_index['Bizday'] = New_result_Sum_weekdays_without_index.groupby('Month')[
        'FailureTaskGeneratedTime'].rank("dense", ascending=True)
    New_result_Sum_weekdays_without_index = New_result_Sum_weekdays_without_index.set_index('FailureTaskGeneratedTime')
    New_result_Sum_weekdays_without_index = New_result_Sum_weekdays_without_index[
        ['Total', 'Country Weight', 'Weekdays', 'Month', 'Day', 'Bizday']]
    ##'T-1', 這個特徵不行！！！！
    New_result_Sum_weekdays_moving_mean = pd.DataFrame()
    New_result_Sum_weekdays_moving_mean['Moving'] = New_result_Sum_weekdays_without_index['Total'].rolling(
        window=3).mean()
    Country_Weight = New_result_Sum_weekdays_without_index['Country Weight'].rolling(window=2).mean()
    New_result_Sum_weekdays_without_index['Country Weight'] = Country_Weight
    New_result_Sum_weekdays_moving_mean = New_result_Sum_weekdays_moving_mean.dropna(0)

    New_result_Sum_weekdays_updated = pd.merge(New_result_Sum_weekdays_moving_mean,
                                               New_result_Sum_weekdays_without_index, on='FailureTaskGeneratedTime',
                                               how='left')
    New_result_Sum_weekdays_updated = New_result_Sum_weekdays_updated[
        New_result_Sum_weekdays_updated.index > '2018-12-31']

    result_Holiday = result_Holiday[['EMEA', 'US', 'Australasia', 'Canada', 'Latin America', 'Asia']]

    result_Holiday['US'] = (result_Holiday['US'] / result_Holiday['US']).fillna(0) * (
                1 + result_Domicile['US'].fillna(0))  # *float(US_number.values)

    result_Holiday['EMEA'] = (result_Holiday['EMEA'] / result_Holiday['EMEA']).fillna(0) * (
                1 + result_Domicile['EMEA'].fillna(0))  # * float(EMEA_number)

    result_Holiday['Canada'] = (result_Holiday['Canada'] / result_Holiday['Canada']).fillna(0) * (
                1 + result_Domicile['Canada'].fillna(0))  # * float(CAN_number)

    result_Holiday['Australasia'] = (result_Holiday['Australasia'] / result_Holiday['Australasia']).fillna(0) * (
                1 + result_Domicile['AUS'].fillna(0))  # * float(AUS_number)

    result_Holiday['Latin America'] = (result_Holiday['Latin America'] / result_Holiday['Latin America']).fillna(0) * (
                1 + result_Domicile['BRA'].fillna(0))  # * float(BRA_number)*0.0

    result_Holiday['Asia'] = (result_Holiday['Asia'] / result_Holiday['Asia']).fillna(0) * (
                1 + (result_Domicile['KOR'] + result_Domicile['IND']).fillna(
            0))  # * (float(KOR_number) + float(IND_number))*0.0

    # print(dataset_country_Big_ratio.sort_values('InvestmentId', ascending=False).head(7))
    result_Holiday = result_Holiday[['EMEA', 'US', 'Australasia', 'Canada', 'Asia', 'Latin America']].fillna(0)  # ,

    result_Holiday.columns = result_Holiday.columns
    result_Holiday.index.names = ['FailureTaskGeneratedTime']

    New_result_Sum_weekdays_holiday_updated = New_result_Sum_weekdays_updated.reset_index()

    result_Holiday_without_index = result_Holiday.reset_index()
    result_Holiday_without_index2 = pd.merge(New_result_Sum_weekdays_holiday_updated, result_Holiday_without_index,
                                             on='FailureTaskGeneratedTime', how='left')
    # New_result_Sum_weekdays_updated.head()
    New_result_Sum_weekdays_updated = result_Holiday_without_index2.set_index('FailureTaskGeneratedTime')
    New_result_Sum_weekdays_updated2 = New_result_Sum_weekdays_updated[['Total', 'Moving', 'Weekdays', 'Month', 'Day',
                                                                        'Bizday', 'EMEA', 'US', 'Australasia', 'Canada',
                                                                        'Asia']]  # 'Moving','Country Weight',,'Latin America'
    # New_result_Sum_weekdays_updated.columns
    New_result_Sum_weekdays_updated2 = New_result_Sum_weekdays_updated2.fillna(0)

    # split_date = '2019-12-01'

    Failure_Number_Test = New_result_Sum_weekdays_updated  # .loc[New_result_Sum_weekdays_updated.index > split_date].copy().fillna(0)
    Failure_Number_Test = Failure_Number_Test[['Total', 'Moving', 'Weekdays', 'Month', 'Day', 'Bizday', 'EMEA', 'US',
                                               'Australasia', 'Canada', 'Asia']]
    X_test = Failure_Number_Test.drop(['Total'], axis=1).values
    # load saved model

    # 报错原因是新DataFrame中字段的顺序和之前的不一样。
    loaded_model = joblib.load(r'C:\Users\Mma4\Desktop\FailuresReport\xgboostModel')
    pre_value = loaded_model.predict(X_test)
    return pre_value




