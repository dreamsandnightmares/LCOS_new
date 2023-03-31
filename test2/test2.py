import math

import numpy as np

from data_load.data_load import data_load
from PV.PVModel import PVSystem
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from HT.hydrogenStorage import HT
from price.gridPrice import grid_price
from bt.MABattey import LionBattery
from EMS.BEMS import BEMS


import matplotlib.pyplot as plt
import math



def ssr(P_grid, P_load):
    return (1 - (P_grid / P_load))

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


def NPV(r_0, r_bess, cost_bt, cost_h2, cost_el, cost_fc, li_cap, h2_cap, el_cap
        , fc_cap, cost_om, project_time):
    npv = 0
    cost_cap_bt = cost_bt * li_cap
    cost_cap_h2 = cost_h2 * h2_cap
    cost_cap_fc = cost_fc * fc_cap
    cost_cap_el = cost_el * el_cap
    cost_cap = cost_cap_el + cost_cap_bt + cost_cap_fc + cost_cap_h2
    for i in range(project_time):

        if i == 11:
            cost_rep = 0.60 * cost_cap_bt

            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        elif i == 5:
            cost_rep = cost_fc * 0.775
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        elif i == 15:
            cost_rep = cost_fc * 0.55 + cost_el * 0.6
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        elif i == 20:
            cost_rep = cost_fc * 0.325
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        elif i == 25:
            cost_rep = cost_fc * 0.1
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        else:
            cost_rep = 0
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap

    return npv


def NPV_Bess(r_0, r_bess, cost_pv, cost_bt, li_cap, pv_cap, project_time):
    npv = 0
    cost_cap_bt = cost_bt * li_cap
    cost_cap_pv = pv_cap * cost_pv
    cost_om = cost_cap_bt * 0.005 + cost_cap_pv * 0.01

    # print(cost_om,'om')
    #
    # print(r_0,'r_init')
    # print(r_bess,'r_bess')

    cost_cap = cost_cap_bt + cost_cap_pv
    # print(cost_cap,'cap')
    for i in range(project_time):

        if i == 11:
            cost_rep = 0.60 * cost_cap_bt

            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i)
            # print(((r_0-r_bess) - cost_om - cost_rep) /math.pow((1+0.05),i),'rep')

        else:
            cost_rep = 0
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i)
            # print(((r_0-r_bess) - cost_om - cost_rep) /math.pow((1+0.05),i),'not rep')
    # print(npv)
    npv = npv - cost_cap

    return npv


def lcos(cost_pv, cost_bt, li_cap, pv_cap, project_time, ele, wout):
    cost_cap_bt = cost_bt * li_cap
    cost_cap_pv = pv_cap * cost_pv
    cost_om = cost_cap_bt * 0.005 + cost_cap_pv * 0.01
    at = 0
    wout_all = 0
    cost_cap = cost_cap_bt + cost_cap_pv

    for i in range(project_time):
        if i == 11:
            cost_rep = 0.60 * cost_cap_bt

            at += (cost_om + cost_rep + 0.3 * ele) / math.pow((1 + 0.05), i)

            wout_all = wout / math.pow((1 + 0.05), i)
    return (cost_cap + at) / wout_all


def lcoe(cost_pv, cost_bt, li_cap, pv_cap, project_time, energy,ele_cost):
    cost_cap_bt = cost_bt * li_cap
    cost_cap_pv = pv_cap * cost_pv
    cost_om = cost_cap_bt * 0.005 + 19 * pv_cap
    d = 0.05
    down = 0
    cost_om_all = 0
    cost_rep = 0.60 * cost_cap_bt
    cost_cap = cost_cap_bt + cost_cap_pv

    for i in range(project_time):
        cost_om_all += cost_om / (math.pow((1 + d), i))

        down += (energy / (math.pow((1 + d), i)))
    lcoe_ = (cost_cap + cost_om_all + cost_rep - 0.5 * cost_cap+ele_cost) / down
    return lcoe_

def energy_management(project_lifetime:int,life_time:int,bt:np.array,pv_output:np.array,pd_load):
    res_output = pv_output


    ems  = BEMS(bt=bt)
    ems.initializa()
    ele_cost = 0
    soc_ = []
    gridTopower = 0
    stoTopower = 0
    energyTosto = 0
    energy_BESS = []
    energy_BESS_OLDS = []
    soc_BESS = []
    soc_BESS_OLDS = []
    ele_all = 0
    energy_sto = []
    energy_sto_dis = []
    for y in range(project_lifetime):
        for i in range(life_time):


            energy = res_output[i] - pd_load[i]
            print(energy)
            soc_.append(bt.readSoc())
            soc_BESS.append(bt.readSoc())
            ele, sto, eTs = ems.energyStorage(energy)
            gridTopower += ele
            stoTopower += sto
            energyTosto += eTs
            energy_BESS.append(ele)
            ele_cost += ele * grid_price(i)
            ele_all += pd_load[i]
            energy_sto.append(eTs)
            energy_sto_dis.append(sto)
    return gridTopower/project_lifetime,stoTopower/project_lifetime,energyTosto/project_lifetime,ele_cost/project_lifetime,ele_all/project_lifetime

def fitness(pv_cap,bt_cap,cost_pv,cost_bt,project_lifetime,life_time):
    pv, bt, pd_load, pd_price, pv_output, R_init = device_init(pv_cap=pv_cap, bt_cap=bt_cap)
    gridTopower, stoTopower, energyTosto, ele_cost, ele_all = energy_management(project_lifetime=project_lifetime,
                                                                                life_time=life_time, bt=bt,
                                                                                pv_output=pv_output, pd_load=pd_load, )

    Lcoe = lcoe(cost_pv=cost_pv, cost_bt=cost_bt, li_cap=bt_cap, pv_cap=pv_cap, project_time=project_lifetime,
                energy=(ele_all - gridTopower), ele_cost=ele_cost)
    SSR = ssr(gridTopower, ele_all)
    obj =np.array([Lcoe,SSR])


    return obj












if __name__ == '__main__':
    pv_cap = 3000
    bt_cap = 3000
    project_lifetime = 25
    life_time = 8760
    cost_pv = 5000
    cost_bt = 1900

    in_ = np.array([[3000,2000],[2000,1000]])
    a = np.append(in_, in_)
    print(a)










    # LCOE,SSR =fitness(pv_cap=pv_cap,bt_cap=bt_cap,project_lifetime=project_lifetime,life_time=life_time,cost_bt=cost_bt,cost_pv=cost_pv)
    # print(LCOE,SSR)
    #
    # pv, bt, pd_load, pd_price, pv_output, R_init = device_init(pv_cap=pv_cap,bt_cap=bt_cap)
    # gridTopower, stoTopower, energyTosto, ele_cost, ele_all = energy_management(project_lifetime=project_lifetime,life_time=life_time,bt=bt,
    #                                                                             pv_output =pv_output,pd_load=pd_load,)
    #
    # Lcoe =lcoe(cost_pv= cost_pv,cost_bt=cost_bt,li_cap=bt_cap,pv_cap=pv_cap,project_time=project_lifetime,energy=(ele_all - gridTopower),ele_cost=250576)
    # SSR = ssr(gridTopower,ele_all)
    # print(Lcoe)
    # print(SSR)
    # print(ele_all)
    # p  = 0
    # print(len(pd_load))
    # for i in range(len(pd_load)):
    #     p+= pd_load[i]*grid_price(i)
    # print(p/ele_all,'电价')

