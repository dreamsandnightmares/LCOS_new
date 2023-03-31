'外送电路问题  '
'效率问题'
'适用场景问题'

'为什么充电变多了BESS OLDS'

from PV.PVModel import PVSystem
import numpy as np
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from HT.hydrogenStorage import HT
from price.gridPrice import grid_price
from data_load.data_load import data_load
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


class BEMS(object):
    def __init__(self, bt: LionBattery):
        self.bt = bt
        self.len =len(bt.readSoc())
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)

    def initializa(self):
        self.bt.initializa()
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)

    def energyStorage(self, energy):
       for i in range(len(energy)):
           P_BT_dc = np.zeros([self.bt.len_]  )
           P_BT_ch = np.zeros([self.bt.len_]  )

           if energy[i] >= 0:

                # print(energy[i])

                '充电过程'
                max_charge = self.bt.max_charge()[i]
                if energy[i] <= max_charge:
                    P_BT_ch[i] = energy[i]
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)

                    self.GridToEnergy[i] = 0
                    self.storageToEnergy[i] =0
                    self.energyToStorage[i] =energy[i]
                else:
                    P_BT_ch[i] = max_charge
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)
                    self.GridToEnergy[i] = 0
                    self.storageToEnergy[i] = 0
                    self.energyToStorage [i]=max_charge
           elif energy[i] < 0:
                P_BT_dc = np.zeros([self.bt.len_])
                P_BT_ch = np.zeros([self.bt.len_])
                '放电过程'
                SOC = self.bt.readSoc()[i]
                # print(SOC,'SOC')
                # print(self.bt.SOC_min)
                if SOC > self.bt.SOC_min[i]:
                    max_discharge = self.bt.max_discharge()[i]
                    # print(type(max_discharge))
                    # print(max_discharge[i,:])

                    if abs(energy[i]) <= max_discharge:

                        P_BT_dc[i] = abs(energy[i])
                        self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                        self.bt.soc(i)
                        self.GridToEnergy[i] = 0
                        self.storageToEnergy[i] = abs(energy[i])
                        self.energyToStorage[i] = 0
                    else:
                        P_BT_dc[i] = max_discharge
                        self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                        self.bt.soc(i)
                        self.GridToEnergy[i] =abs(energy[i]) - max_discharge
                        self.storageToEnergy[i] =  max_discharge
                        self.energyToStorage[i] =  0
                else:
                    P_BT_dc = np.zeros([self.bt.len_])
                    P_BT_ch = np.zeros([self.bt.len_])
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)
                    self.GridToEnergy[i] =  abs(energy[i])
                    self.energyToStorage[i] = 0
                    self.storageToEnergy[i] = 0


       return self.GridToEnergy, self.storageToEnergy, self.energyToStorage


class BEMS_OLDS(object):
    def __init__(self, bt: LionBattery, t_start, t_end, LIMIT_SUNNY, LIMIT_CLOUDY):
        self.bt = bt
        self.t_start = t_start
        self.t_end = t_end
        self.LIMIT_SUNNY = LIMIT_SUNNY
        self.LIMIT_CLOUDY = LIMIT_CLOUDY
        self.peak_enable = False

        self.len = len(bt.readSoc())
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)
        self.dis_enable = np.array([True] * self.len)

    def initializa(self):
        self.bt.initializa()

        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)

        self.dis_enable = np.array([True]*self.len)

    def enable(self, time,i):

            SOC = self.bt.readSoc()[i]
            if self.t_start <= time <= self.t_end:
                if SOC > self.LIMIT_CLOUDY:
                    self.dis_enable[i] = True
                else:
                    self.dis_enable[i] = False
            else:
                if SOC > self.LIMIT_SUNNY:
                    self.dis_enable[i] = True
                else:
                    self.dis_enable[i] = False


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
        for i in range(self.len):
            P_BT_dc = np.zeros([self.bt.len_])
            P_BT_ch = np.zeros([self.bt.len_])
            if energy[i] >= 0:
                "充电过程"
                max_charge = self.bt.max_charge()[i]
                if energy[i] < max_charge:
                    P_BT_ch[i] = energy[i]

                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)

                    self.enable(time,i)

                    self.storageToEnergy[i] = 0
                    self.energyToStorage[i] = energy[i]
                    self.GridToEnergy[i] = 0
                else:
                    P_BT_ch[i] = max_charge
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)
                    self.enable(time,i)

                    self.energyToStorage[i] = max_charge
                    self.storageToEnergy[i] = 0
                    self.GridToEnergy[i] = 0

            else:
                '放电过程'
                "所有energy 要取绝对值"
                P_BT_dc = np.zeros([self.bt.len_])
                P_BT_ch = np.zeros([self.bt.len_])

                if self.t_start <= time <= self.t_end:
                        SOC = self.bt.readSoc()[i]
                        if SOC > self.LIMIT_CLOUDY:
                            self.if_peak(time)
                            if self.peak_enable:
                                max_discharge = self.bt.max_discharge_limit(self.LIMIT_CLOUDY)[i]
                                if abs(energy[i]) <= max_discharge:
                                    P_BT_dc[i] = abs(energy[i])

                                    self.bt.StateOfCharge1(P_BT_dc=P_BT_dc, P_BT_ch=P_BT_ch)
                                    self.bt.soc(i)
                                    self.enable(time,i)

                                    self.energyToStorage[i] = 0
                                    self.storageToEnergy[i] = abs(energy[i])
                                    self.GridToEnergy[i] = 0
                                else:
                                    P_BT_dc[i] = max_discharge
                                    self.bt.StateOfCharge1(P_BT_dc=P_BT_dc, P_BT_ch=P_BT_ch)
                                    self.bt.soc(i)
                                    self.enable(time,i)

                                    self.energyToStorage[i] = 0
                                    self.GridToEnergy [i]= abs(energy[i]) - max_discharge
                                    self.storageToEnergy[i] = max_discharge
                            else:
                                    self.GridToEnergy[i] = abs(energy[i])
                                    self.energyToStorage[i] = 0
                                    self.storageToEnergy[i] = 0
                        else:
                            self.GridToEnergy[i] = abs(energy[i])
                            self.energyToStorage[i] = 0
                            self.storageToEnergy[i] = 0

                else:

                        P_BT_dc = np.zeros([self.bt.len_])
                        P_BT_ch = np.zeros([self.bt.len_])
                        SOC = self.bt.readSoc()[i]
                        if SOC > self.LIMIT_SUNNY:

                            max_discharge = self.bt.max_discharge_limit(self.LIMIT_SUNNY)[i]

                            if abs(energy[i]) <= max_discharge:
                                    P_BT_dc[i]= abs(energy[i])

                                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                                    self.bt.soc(i)

                                    self.energyToStorage[i] = 0
                                    self.GridToEnergy[i] = 0
                                    self.storageToEnergy[i] = abs(energy[i])

                                    self.enable(time,i)
                            else:
                                    P_BT_dc[i] = max_discharge
                                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                                    self.bt.soc(i)
                                    self.enable(time,i)

                                    self.energyToStorage[i] = 0
                                    self.GridToEnergy[i] = abs(energy[i]) - max_discharge
                                    self.storageToEnergy[i] = max_discharge

                        else:
                            self.GridToEnergy[i] = abs(energy[i])
                            self.energyToStorage[i] = 0
                            self.storageToEnergy[i] = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage


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