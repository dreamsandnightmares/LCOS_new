import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate.interpolate import make_interp_spline

def data_load():
    path = r"C:\Users\王晨浩\Desktop\LCOS\Data"
    # path = r"../RECO_data"
    # print(os.listdir(path))
    # path = 'RECO_data'
    # print(os.listdir(path))
    FileNames = os.listdir(path)

    # print(FileNames)
    x = pd.DataFrame()
    for name in  FileNames:
        if re.search('jcpl',name):
            full_name = os.path.join(path, name)
            data = pd.read_csv(full_name,encoding='utf-8')
            x= pd.concat([x,data])
            pd_price= x['JCPL'].tolist()
            for i in  range(len(x)):
                if float(pd_price[i].strip("$")) >100:

                    pd_price[i]  =100
                else:
                    pd_price[i] = float(pd_price[i].strip("$"))
            for i in range(len(pd_price)):
                # if pd_price[i]>70:
                #     pd_price[i] = 70
                pass

    return pd_load,pd_price,pd_wea_wind,pd_wea_G_dir,pd_wea_G_diff,pd_wea_T,pd_wea_G_hor