import os
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate.interpolate import make_interp_spline
from PV.PVModel import PVSystem



#

#
# FileNames =os.listdir(path)

def data_load():
    path = r"/home/wch/Desktop/LCOS/RECO_data"
    # path = r"../RECO_data"
    # print(os.listdir(path))
    # path = 'RECO_data'
    # print(os.listdir(path))
    FileNames = os.listdir(path)

    # print(FileNames)
    x = pd.DataFrame()
    for name in  FileNames:

        if re.search('Load',name):
            full_name =os.path.join(path,name)
            pd_load =pd.read_csv(full_name,encoding='utf-8')
            pd_load = pd_load['mw'].tolist()
            for i in range(len(pd_load)):
                pd_load[i] =pd_load[i]/4.5
        elif re.search('jcpl',name):
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

        else:
            full_name = os.path.join(path,name)

            pd_wea = pd.read_csv(full_name,encoding='utf-8')
            pd_wea_T = pd_wea['气温℃'].tolist()
            pd_wea_G_dir = pd_wea['直接辐射W/m^2'].tolist()
            pd_wea_G_diff = pd_wea['散射辐射W/m^2'].tolist()
            pd_wea_wind = pd_wea['地面风速m/s'].tolist()

            pd_wea_G_hor = pd_wea['地表水平辐射W/m^2'].tolist()

    return pd_load,pd_price,pd_wea_wind,pd_wea_G_dir,pd_wea_G_diff,pd_wea_T,pd_wea_G_hor


if __name__ == '__main__':
    pv_cap = 250
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()
    pv =PVSystem(pv_cap,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)
    fc_energy  =[]
    for i  in range(8760):
        energy = pd_load[i]  - pv.PVpower(i)
        if energy >=0:
            fc_energy.append(energy)
    print(max(fc_energy),'max')
    print(min(fc_energy),'min')



