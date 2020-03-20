#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pyodbc
import pandas as pd
import numpy as np
import sys
import pandas as pd
from pyecharts import Pie,Timeline,Bar,Overlap,Line
import random
import numpy as np
from pandas import DataFrame,Series
from pyecharts import configure
import time


import re
import warnings



def time_value(dec):
    def TimeCost(*args,**kwargs):
        start = time.time()
        get_str = dec(*args,**kwargs)
        end = time.time()
        print("Function Total Time Cost：",end-start)
        return get_str
    return TimeCost

class Raw_Data(object):
    def __init__(self,path1,path2):
        self.path1=path1
        self.path2=path2

    @time_value
    def Concat(self):   
        return pd.concat([pd.read_csv(self.path1),pd.read_csv(self.path2)],axis = 0)

@time_value
def replace_str(List_old,Remove,Updated):

    List_updated = []
    for ID in List_old:
        try:
            ID = ID.replace(Remove, Updated)
        except:
            ID = ID
        List_updated.append(ID)
        
    return List_updated



@time_value
def key_grouper(**kwargs):
    if len(kwargs) == 5:
    
        grouper_ongoing_histroical= kwargs['df'].groupby([pd.Grouper(kwargs['index']),kwargs['level_1'] ,kwargs['level_2']]) 

        result_ongoing_histroical = grouper_ongoing_histroical[kwargs['index']].count().unstack([ kwargs['level_1'],kwargs['level_2']]).fillna(0)

        result_ongoing_histroical = result_ongoing_histroical.resample(kwargs['fre']).sum()
        
    if len(kwargs) == 4:
        
        grouper_ongoing_histroical= kwargs['df'].groupby([pd.Grouper(kwargs['index']),kwargs['level_1']]) 

        result_ongoing_histroical = grouper_ongoing_histroical[kwargs['index']].count().unstack( kwargs['level_1']).fillna(0)

        result_ongoing_histroical = result_ongoing_histroical.resample(kwargs['fre']).sum()
        
    if len(kwargs) == 6:
        
        grouper_ongoing_histroical= kwargs['df'].groupby([pd.Grouper(kwargs['index']),kwargs['level_1'] ,kwargs['level_2'] ,kwargs['level_3']]) 

        result_ongoing_histroical = grouper_ongoing_histroical[kwargs['index']].count().unstack([ kwargs['level_1'],kwargs['level_2'],kwargs['level_3']]).fillna(0)

        result_ongoing_histroical = result_ongoing_histroical.resample(kwargs['fre']).sum()
        
        
    return result_ongoing_histroical


# In[ ]:




