from PV.PVModel import PVSystem
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from HT.hydrogenStorage import HT
from obj.obj_function import ssr,NPV,NPV_Bess,lcos,lcoe
from price.gridPrice import grid_price
from data_load.data_load import data_load
from EMS.BEMS import BEMS
from EMS.BEMS import BEMS_OLDS
from EMS.HEMS import HEMS
from EMS.HEMS import HEMS_OLDS
from EMS.HybridESS import HybridESS
from EMS.HybridESS import HybridESS_OLDS
from bt.MABattey import LionBattery


import matplotlib.pyplot as plt
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

    pv_cap  = 250
    pv =PVSystem(pv_cap,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)

    bt_cap = 600
    bt = LionBattery(bt_cap,eta_BT_conv=0.98)
    bt.initializa()

    el_cap = 15
    el  =PEM()
    el_n = math.ceil(el_cap/el.max_power())

    fc_cap =15
    fc = PEMFC()
    fc_n  =math.ceil(fc_cap/fc.max_power())

    ht_cap = 3000
    ht = HT(ht_cap)
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
    ems =BEMS(bt=bt)
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
            ele,sto,eTs = ems.energyStorage(energy)
            gridTopower+=ele
            stoTopower +=sto
            energyTosto +=eTs

            ele_cost += ele*grid_price(i)




    SSR = ssr(P_grid=gridTopower,P_load=sum(pd_load)*25)
    npv =NPV_Bess(R_init,cost_bt=2000,pv_cap=250,cost_pv=6950,li_cap=600,project_time=25,r_bess=ele_cost/25)
    print(npv)
    lc = lcos(cost_bt=2000,pv_cap=250,cost_pv=6950,li_cap=600,project_time=25,ele=energyTosto,wout=stoTopower)

    print(lc)
    lcoe_ =lcoe(cost_bt=0,pv_cap=250,cost_pv=1073,li_cap=0,project_time=30,energy=sum(pv_output))
    print(lcoe_)
    print(sum(pv_output))
    plt.plot(list(range(len(pv_output))),pv_output)
    plt.show()


    # plt.plot(list(range(len(soc_))),soc_)
    # plt.show()
    # print(bt.readSoc())
    # print(bt.max_charge())
    # energy = ems.energyStorage(386.690)
    # print(bt.readSoc())
    # energy = ems.energyStorage(-100)
    # print(bt.readSoc())
















