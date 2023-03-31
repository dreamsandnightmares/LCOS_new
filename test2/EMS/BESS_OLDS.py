
from PV.PVModel import PVSystem
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from HT.hydrogenStorage import HT
from price.gridPrice import grid_price
from data_load.data_load import data_load
from EMS.BEMS import BEMS_OLDS
from test2.bt.bt_test import LionBattery

import math
'''
project time 20:
光+储 ： 0.065
光    ： 0.038


project time 30:
光+储 ：0.054 
光    ：0.031

光伏系统验证完成


'''

'实例化设备'

def device_init():
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

    pv_cap  = 3000
    pv =PVSystem(pv_cap,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)

    bt_cap = 2000
    bt = LionBattery(bt_cap,eta_BT_conv=0.98)
    bt.initializa()

    el_cap = 15
    el  =PEM()
    el_n = math.ceil(el_cap/el.max_power())

    fc_cap =15
    fc = PEMFC()
    fc_n  =math.ceil(fc_cap/fc.max_power())

    ht_cap = 3000
    ht = HT(ht_cap, eta_FC=0.6, eta_EL=0.86, delta_t=1)
    ht.initializa()
    pv_output =[]
    R_init = 0
    for i in range(8760):
        pv_output.append(pv.PVpower(i))
        R_init +=pd_load[i]*grid_price(i)



    return pv,bt,el,el_n,fc,fc_n,ht,pd_load,pd_price,pv_output,R_init



if __name__ == '__main__':
    'laod/4.5'
    pv, bt, el, el_n, fc, fc_n, ht,pd_load,pd_price,pv_output,R_init= device_init()
    project_lifetime = 25
    life_time =8760
    ems =BEMS_OLDS(bt=bt,t_start=0,t_end=1000,LIMIT_SUNNY=0.20,LIMIT_CLOUDY=0.25,)
    ems.initializa()
    ele_cost =0
    soc_ = []
    gridTopower = 0
    stoTopower= 0
    energyTosto= 0


    for y in range(project_lifetime):
        for i in range(life_time):

            energy = pv_output[i] - pd_load[i]


            soc_.append(bt.readSoc())
            # ele,sto,eTs = ems.energyStorage(energy,i)
            # gridTopower+=ele
            # stoTopower +=sto
            # energyTosto +=eTs
            #
            # ele_cost += ele*grid_price(i)

            ele,sto, eTs = ems.energyStorage(energy,i)
            print(stoTopower, 'energy sto')
            print(energyTosto, 'sto discharge')
            print(ele, 'gridTopower')
            gridTopower +=ele
            ele_cost +=ele*grid_price(i)
            stoTopower += sto
            energyTosto += eTs


    print('BESS_OLDS')
    print(ele_cost,'grid price')
    print(stoTopower,'energy sto')
    print(energyTosto,'sto discharge')
    print(gridTopower,'gridTopower')




    # plt.plot(list(range(len(soc_))),soc_)
    # plt.show()
    # print(bt.readSoc())
    # print(bt.max_charge())
    # energy = ems.energyStorage(386.690)
    # print(bt.readSoc())
    # energy = ems.energyStorage(-100)
    # print(bt.readSoc())