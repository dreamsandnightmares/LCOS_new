from PV.PVModel import PVSystem
import numpy as np
from price.gridPrice import grid_price
from data_load.data_load import data_load
from test2.bt.bt_test import LionBattery


def device_init(in_:np.array):
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

    pv_cap  = in_[:,0]
    print(pv_cap,'PV_CAP')
    pv =PVSystem(pv_cap,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)

    bt_cap = in_[:,1]
    print(bt_cap,'BT_CAP')
    bt = LionBattery(bt_cap,eta_BT_conv=0.98)
    bt.initializa()
    pv_output =[]
    R_init = 0
    for i in range(8760):
        pv_output.append(pv.PVpower(i))
        R_init +=pd_load[i]*grid_price(i)



    return pv,bt,pd_load,pd_price,pv_output,R_init

if __name__ == '__main__':
    project_lifetime = 25
    life_time = 8760
    in_ = np.array([[3000, 2000], [2000, 1000]])
    print(in_)
    pv, bt, pd_load, pd_price, pv_output, R_init = device_init(in_)
    print(pv_output[2])


    a = 0
    a = np.append(a,0)
    print(a)
    print(bt.SOC_min)
    print(bt.StateOfCharge(P_BT_dc=[0,0],P_BT_ch=[0,0]))
    print(bt.SOC_t)
