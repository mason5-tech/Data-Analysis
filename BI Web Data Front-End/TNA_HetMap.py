#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from pyecharts import Map, Geo

import matplotlib.pyplot as plt
from io import BytesIO
from lxml import etree
import base64
import matplotlib.dates as mdates
import datetime as dt

class Hetmap():

	def __init__(self,data):

		self.data = data

	def graphing(self):
	
		df = self.data

		html1 = df.to_html(formatters={'Name': lambda x: '<b>' + x + '</b>'})

		df2 = df[df.index == 15]
		df3 = df2.iloc[:,1:]

		df3 = df3.rename(columns = {'KOR':'Korea', 'LUX':'Luxembourg', 'IRL':'Ireland', 'USA': 'United States', 'CAN':'Canada', 'GBR':'United Kingdom', 'CHN':'China'})

		list_name = df3.columns
		TNA_value = df3.values.astype(str)
		value = []
		country = []
		for name in list_name:
    			country.append(name) 

		for TNA in TNA_value:
   			value.append(TNA)

		attr= country

		map0 = Map("Mstar HetMap", width=1000, height=600)
		map0.add("Mstar HetMap", attr, value[0], maptype="world",  is_visualmap=True, visual_text_color='#000',visual_range=  [0, 30000])
		map0.render(path="/Users/kguan/Desktop/Python3.6/AI Study Group//html/one Year/TNA HetMap.html")

data = pd.read_excel(r'C:\Users\Mma4\Desktop\TNA failure\RawData.xls')

hmap = Hetmap(data)

hmap.graphing()
