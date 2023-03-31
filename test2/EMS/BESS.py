'外送电路问题  '
import numpy as np
import matplotlib.pyplot as plt

'效率问题'
'适用场景问题'

'为什么充电变多了BESS OLDS'

from PV.PVModel import PVSystem
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from HT.hydrogenStorage import HT
from price.gridPrice import grid_price
from data_load.data_load import data_load
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


class BEMS(object):
    def __init__(self, bt: LionBattery):
        self.bt = bt
        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

    def initializa(self):
        self.bt.initializa()
        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

    def energyStorage(self, energy):

        if energy >= 0:
            '充电过程'
            max_charge = self.bt.max_charge()
            if energy <= max_charge:
                self.bt.StateOfCharge(P_BT_ch=energy, P_BT_dc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = energy
            else:

                self.bt.StateOfCharge(P_BT_ch=max_charge, P_BT_dc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = max_charge
        elif energy < 0:
            '放电过程'
            SOC = self.bt.readSoc()
            if SOC > self.bt.SOC_min:
                max_discharge = self.bt.max_discharge()
                if abs(energy) <= max_discharge:
                    self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=abs(energy))
                    self.GridToEnergy = 0
                    self.storageToEnergy = abs(energy)
                    self.energyToStorage = 0
                else:

                    self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=max_discharge)
                    self.GridToEnergy = abs(energy) - max_discharge
                    self.storageToEnergy = max_discharge
                    self.energyToStorage = 0
            else:
                self.GridToEnergy = abs(energy)
                self.energyToStorage = 0
                self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage


class BEMS_OLDS(object):
    def __init__(self, bt: LionBattery, t_start, t_end, LIMIT_SUNNY, LIMIT_CLOUDY):

        self.bt = bt
        self.GridToEnergy = 0
        self.t_start = t_start
        self.t_end = t_end
        self.LIMIT_SUNNY = LIMIT_SUNNY
        self.LIMIT_CLOUDY = LIMIT_CLOUDY

        self.dis_enable = True
        self.peak_enable = False

    def initializa(self):
        self.bt.initializa()

        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

        self.dis_enable = True

    def enable(self, time):
        SOC = self.bt.readSoc()
        if self.t_start <= time <= self.t_end:
            if SOC > self.LIMIT_CLOUDY:
                self.dis_enable = True
            else:
                self.dis_enable = False
        else:
            if SOC > self.LIMIT_SUNNY:
                self.dis_enable = True
            else:
                self.dis_enable = False


    def if_peak(self, time):
        if 5 <= int(time / (30 * 24)) < 9 or int(time / (30 * 24)) == 10:
            if 12 <= time % 24 < 14 or 8 <= time % 24 < 12 or 14 <= time % 24 < 15 or 18 <= time % 24 < 21:
                self.peak_enable = True
            else:
                self.peak_enable = False
        elif int(time / (30 * 24)) == 9:
            if 8 <= time % 24 < 15 or 18 <= time % 24 < 21:
                self.peak_enable = True
            else:
                self.peak_enable = False
        elif int(time / (30 * 24)) == 12 or int(time / 30 / 24) == 1:
            if 19 <= time % 24 < 21 or 8 <= time % 24 < 11 or 18 <= time % 24 < 19:
                self.peak_enable = True
            else:
                self.peak_enable = False
        else:
            if 8 <= time % 24 < 11 or 18 <= time % 24 < 19:
                self.peak_enable = True
            else:
                self.peak_enable = False
        return self.peak_enable

    def energyStorage(self, energy, time):
        if energy >= 0:
            "充电过程"
            max_charge = self.bt.max_charge()
            if energy < max_charge:
                self.bt.StateOfCharge(P_BT_ch=energy, P_BT_dc=0)
                self.enable(time)

                self.storageToEnergy = 0
                self.energyToStorage = energy
                self.GridToEnergy = 0
            else:
                self.bt.StateOfCharge(P_BT_ch=max_charge, P_BT_dc=0)
                self.enable(time)

                self.energyToStorage = max_charge
                self.storageToEnergy = 0
                self.GridToEnergy = 0

        else:
            '放电过程'
            "所有energy 要取绝对值"
            energy = abs(energy)
            if self.t_start <= time <= self.t_end:
                SOC = self.bt.readSoc()
                if SOC > self.LIMIT_CLOUDY:
                    self.if_peak(time)
                    if self.peak_enable:
                        max_discharge = self.bt.max_discharge_limit(self.LIMIT_CLOUDY)
                        if energy <= max_discharge:
                            self.bt.StateOfCharge(P_BT_dc=energy, P_BT_ch=0)
                            self.enable(time)

                            self.energyToStorage = 0
                            self.storageToEnergy = energy
                            self.GridToEnergy = 0
                        else:
                            self.bt.StateOfCharge(P_BT_dc=max_discharge, P_BT_ch=0)
                            self.enable(time)

                            self.energyToStorage = 0
                            self.GridToEnergy = energy - max_discharge
                            self.storageToEnergy = max_discharge
                    else:
                            self.GridToEnergy = energy
                            self.energyToStorage = 0
                            self.storageToEnergy = 0
                else:
                    self.GridToEnergy = energy
                    self.energyToStorage = 0
                    self.storageToEnergy = 0

            else:
                SOC = self.bt.readSoc()
                if SOC > self.LIMIT_SUNNY:
                    if self.dis_enable == True:
                        max_discharge = self.bt.max_discharge_limit(self.LIMIT_SUNNY)
                        if energy <= max_discharge:
                            self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=energy)

                            self.energyToStorage = 0
                            self.GridToEnergy = 0
                            self.storageToEnergy = energy

                            self.enable(time)
                        else:
                            self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=max_discharge)
                            self.enable(time)

                            self.energyToStorage = 0
                            self.GridToEnergy = energy - max_discharge
                            self.storageToEnergy = max_discharge
                    else:
                        self.GridToEnergy = energy
                        self.energyToStorage = 0
                        self.storageToEnergy = 0
                else:
                    self.GridToEnergy = energy
                    self.energyToStorage = 0
                    self.storageToEnergy = 0

            #
            # if SOC > self.bt.SOC_min:
            #     if self.dis_enable == True:
            #         max_discharge = self.bt.max_discharge_limit(self.LIMIT_CLOUDY)
            #         if energy <= max_discharge:
            #             self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=energy)
            #
            #             self.energyToStorage = 0
            #             self.GridToEnergy = 0
            #             self.storageToEnergy = energy
            #
            #             self.enable(time)
            #         else:
            #             self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=max_discharge)
            #             self.enable(time)
            #
            #             self.energyToStorage = 0
            #             self.GridToEnergy = energy - max_discharge
            #             self.storageToEnergy = max_discharge
            #
            #     else:
            #         if self.t_start <= time <= self.t_end:
            #             '定义 t_start - t_end 为光伏为0的时间'
            #             '储能系统仅在 电价贵的时候放电'
            #             self.if_peak(time)
            #             if self.peak_enable:
            #                 max_discharge = self.bt.max_discharge()
            #                 if energy <= max_discharge:
            #                     self.bt.StateOfCharge(P_BT_dc=energy, P_BT_ch=0)
            #                     self.enable(time)
            #
            #                     self.energyToStorage = 0
            #                     self.storageToEnergy = energy
            #                     self.GridToEnergy = 0
            #                 else:
            #                     self.bt.StateOfCharge(P_BT_dc=max_discharge, P_BT_ch=0)
            #                     self.enable(time)
            #
            #                     self.energyToStorage = 0
            #                     self.GridToEnergy = energy - max_discharge
            #                     self.storageToEnergy = max_discharge
            #
            #
            #             else:
            #                 self.GridToEnergy = energy
            #                 self.energyToStorage = 0
            #                 self.storageToEnergy = 0
            #
            # else:
            #     self.GridToEnergy = abs(energy)
            #     self.energyToStorage = 0
            #     self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage


def device_init():
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

    pv_cap  =3000
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
    ht = HT(ht_cap,eta_FC=0.6,eta_EL=0.86,delta_t=1)
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
    print(sum(pv_output), 'pv_output')
    print(sum(pd_load), 'pd_load')
    project_lifetime = 1
    life_time =10
    ems =BEMS(bt=bt)
    ems.initializa()
    ele_cost =0
    soc_ = []
    gridTopower = 0
    stoTopower= 0
    energyTosto= 0
    energy_BESS = []
    energy_BESS_OLDS = []
    soc_BESS =[]
    soc_BESS_OLDS = []
    ele_all =0
    energy_sto =[]
    energy_sto_dis =[]

    for y in range(project_lifetime):
        for i in range(life_time):

            energy = pv_output[i] - pd_load[i]




            soc_.append(bt.readSoc())
            soc_BESS.append(bt.readSoc())
            ele,sto,eTs = ems.energyStorage(energy)
            gridTopower+=ele
            stoTopower +=sto
            energyTosto +=eTs
            energy_BESS.append(ele)
            ele_cost += ele*grid_price(i)
            ele_all +=pd_load[i]
            energy_sto.append(eTs)
            energy_sto_dis.append(sto)



    print('BESS')
    print(ele_cost,'grid price')
    print(stoTopower,'stoTopower')
    print(energyTosto,'energyTosto')
    print(gridTopower, 'gridTopower')

    print('LOAD')
    print(ele_all,'load')
    plt.plot(list(range(len(energy_sto[:200]))),energy_sto[:200],label ='ch')
    plt.plot(list(range(len(energy_sto_dis[:200]))), energy_sto_dis[:200])
    plt.legend()
    plt.show()
    print(sum(energy_sto))
    print(sum(energy_sto_dis))


    'BESS OLDS'
    # pv, bt, el, el_n, fc, fc_n, ht,pd_load,pd_price,pv_output,R_init= device_init()
    # project_lifetime = 25
    # life_time =8760
    # ems =BEMS_OLDS(bt=bt,t_start=0,t_end=1000,LIMIT_SUNNY=0.20,LIMIT_CLOUDY=0.25,)
    # ems.initializa()
    # ele_cost =0
    # soc_ = []
    # gridTopower = 0
    # stoTopower= 0
    # energyTosto= 0
    # energy_ =[]
    # energy_dc =[]
    #
    # ele_test = []
    #
    #
    #
    #
    # for y in range(project_lifetime):
    #     for i in range(life_time):
    #
    #         energy = pv_output[i] - pd_load[i]
    #
    #
    #
    #
    #         soc_.append(bt.readSoc())
    #         soc_BESS_OLDS.append(bt.readSoc())
    #
    #         # ele,sto,eTs = ems.energyStorage(energy,i)
    #         # gridTopower+=ele
    #         # stoTopower +=sto
    #         # energyTosto +=eTs
    #         #
    #         # ele_cost += ele*grid_price(i)
    #
    #         ele,sto, eTs = ems.energyStorage(energy,i)
    #         ele_test.append(ele)
    #         energy_.append(eTs)
    #         energy_dc.append(sto)
    #
    #
    #         gridTopower +=ele
    #         ele_cost +=ele*grid_price(i)
    #         stoTopower += sto
    #         energyTosto += eTs
    #         energy_BESS_OLDS.append(ele)
    #
    #
    # print('BESS_OLDS')
    # print(ele_cost,'grid price')
    # print(stoTopower,'stoTopower')
    # print(energyTosto,'energyTosto')
    # print(gridTopower, 'gridTopower')
    # np.round(2)
    # np.savetxt(r'C:\Users\王晨浩\Desktop\LCOS\test2\EMS\ele_test_bess_olds',ele_test)
    # plt.plot(list(range(len(energy_sto_dis[:200]))), energy_sto_dis[:200], label='HESS')
    # plt.legend()
    # plt.show()
    #
    #
    # # diff =[]
    # # for i in range(len(energy_BESS)):
    # #     diff.append(energy_BESS[i]-energy_BESS_OLDS[i])
    # enable =[]
    # for i in range(200):
    #     if ems.if_peak(i) ==True:
    #         enable.append(1)
    #     else:
    #         enable.append(0)
    #
    # plt.plot(list(range(len(diff[:200]))), diff[:200], label='ebable')
    # print(enable)
    # plt.legend()
    # plt.show()
    # plt.plot(list(range(len(soc_BESS[:200]))),soc_BESS[:200])
    # plt.plot(list(range(len(soc_BESS_OLDS[:200]))), soc_BESS_OLDS[:200],label ='soc_BESS_OLDS')
    # plt.legend()
    # plt.show()
    # # plt.plot(list(range(len(enable))), enable, label='ebable')
    # # print(enable)
    # # plt.legend()
    # # plt.show()
    #
    #
    #





    # SSR = ssr(P_grid=gridTopower,P_load=sum(pd_load)*25)
    # npv =NPV_Bess(R_init,cost_bt=2000,pv_cap=250,cost_pv=6950,li_cap=600,project_time=25,r_bess=ele_cost/25)
    # print(npv)
    # lc = lcos(cost_bt=2000,pv_cap=250,cost_pv=6950,li_cap=600,project_time=25,ele=energyTosto,wout=stoTopower)
    #
    # print(lc)
    # lcoe_ =lcoe(cost_bt=0,pv_cap=250,cost_pv=1073,li_cap=0,project_time=30,energy=sum(pv_output))
    # print(lcoe_)
    # print(sum(pv_output))
    # plt.plot(list(range(len(pv_output))),pv_output)
    # plt.show()


    # plt.plot(list(range(len(soc_))),soc_)
    # plt.show()
    # print(bt.readSoc())
    # print(bt.max_charge())
    # energy = ems.energyStorage(386.690)
    # print(bt.readSoc())
    # energy = ems.energyStorage(-100)
    # print(bt.readSoc())