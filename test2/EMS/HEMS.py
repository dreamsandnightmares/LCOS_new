from PV.PVModel import PVSystem
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from HT.hydrogenStorage import HT
from price.gridPrice import grid_price
from data_load.data_load import data_load
from test2.bt.bt_test import LionBattery


import matplotlib.pyplot as plt
import math
class HEMS(object):
    def __init__(self,ht:HT,el_power,fc_power):
        self.ht =ht
        self.GridToEnergy =0
        self.el = el_power
        self.fc =fc_power

    def initializa(self):
        '初始化'
        self.ht.initializa()
        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0
    def energyStorage(self,energy):
        if energy >= 0:
            '充电过程'
            max_charge = min(self.ht.max_charge(),self.el)
            if energy <= max_charge:
                self.ht.soc(P_el=energy,P_fc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = energy
            else:
                self.ht.soc(P_el=max_charge,P_fc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = max_charge
        elif energy < 0:
            '放电过程'
            SOC = self.ht.readSOC()
            if SOC > self.ht.SOC_Min():
                max_discharge =min(self.ht.max_discharge(),self.fc)
                if abs(energy) <= max_discharge:
                    self.ht.soc(P_el=0, P_fc=abs(energy))
                    self.GridToEnergy = 0
                    self.storageToEnergy = abs(energy)
                    self.energyToStorage = 0
                else:
                    self.ht.soc(P_el=0, P_fc=abs(max_discharge))
                    self.GridToEnergy = abs(energy) - max_discharge
                    self.storageToEnergy = max_discharge
                    self.energyToStorage = 0
            else:
                self.GridToEnergy = abs(energy)
                self.energyToStorage = 0
                self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage





class HEMS_OLDS(object):
    def __init__(self, ht:HT,el_power,fc_power, t_start, t_end, LIMIT_SUNNY, LIMIT_CLOUDY):

        self.ht = ht
        self.GridToEnergy = 0
        self.t_start = t_start
        self.t_end = t_end
        self.LIMIT_SUNNY = LIMIT_SUNNY
        self.LIMIT_CLOUDY = LIMIT_CLOUDY
        self.el =el_power
        self.fc =fc_power

        self.dis_enable = True
        self.peak_enable = False

    def initializa(self):
        self.ht.initializa()

        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

        self.dis_enable = True

    def enable(self, time):
        SOC = self.ht.readSOC()
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
            max_charge = min(self.ht.max_charge(), self.el)
            if energy < max_charge:
                self.ht.soc(P_el=energy, P_fc=0)
                self.enable(time)

                self.storageToEnergy = 0
                self.energyToStorage = energy
                self.GridToEnergy = 0
            else:
                self.ht.soc(P_el=max_charge,P_fc=0)
                self.enable(time)

                self.energyToStorage = max_charge
                self.storageToEnergy = 0
                self.GridToEnergy = 0

        else:
            '放电过程'
            "所有energy 要取绝对值"
            energy = abs(energy)
            if self.t_start <= time <= self.t_end:
                SOC = self.ht.readSOC()
                if SOC > self.LIMIT_CLOUDY:
                    self.if_peak(time)
                    if self.peak_enable:
                        max_discharge =min(self.ht.max_discharge_limit(self.LIMIT_CLOUDY),self.fc)
                        if energy <= max_discharge:
                            self.ht.soc(P_el=0, P_fc=abs(energy))
                            self.enable(time)
                            self.energyToStorage = 0
                            self.storageToEnergy = energy
                            self.GridToEnergy = 0
                        else:
                            self.ht.soc(P_el=0, P_fc=max_discharge)
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
                SOC = self.ht.readSOC()
                if SOC > self.LIMIT_SUNNY:
                    if self.dis_enable == True:
                        max_discharge =min(self.ht.max_discharge_limit(self.LIMIT_SUNNY),self.fc)
                        if energy <= max_discharge:
                            self.ht.soc(P_el=0, P_fc=abs(energy))

                            self.energyToStorage = 0
                            self.GridToEnergy = 0
                            self.storageToEnergy = energy

                            self.enable(time)
                        else:
                            self.ht.soc(P_el=0, P_fc=max_discharge)
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
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage

def device_init():
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

    pv_cap  = 500
    pv =PVSystem(pv_cap,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)

    bt_cap = 600
    bt = LionBattery(bt_cap,eta_BT_conv=0.98)
    bt.initializa()

    el_cap = 500
    el  =PEM()
    el_n = math.ceil(el_cap/el.max_power())

    fc_cap =350
    fc = PEMFC()
    fc_n  =math.ceil(fc_cap/fc.max_power())

    ht_cap = 1000
    ht = HT(ht_cap,eta_FC=0.6,eta_EL=0.96,delta_t=1)
    ht.initializa()
    pv_output =[]
    R_init = 0
    for i in range(8760):
        pv_output.append(pv.PVpower(i))
        R_init +=pd_load[i]*grid_price(i)



    return pv,bt,el,el_n,fc,fc_n,ht,pd_load,pd_price,pv_output,R_init





if __name__ == '__main__':
    el_power =500
    fc_power =350
    pv, bt, el, el_n, fc, fc_n, ht,pd_load,pd_price,pv_output,R_init= device_init()
    project_lifetime = 25
    life_time = 8760
    ems = HEMS(ht=ht,el_power=el_power,fc_power=fc_power)
    ems.initializa()
    ele_cost = 0
    soc_ = []
    gridTopower = 0
    stoTopower = 0
    energyTosto = 0
    energy_HESS = []
    energy_HESS_OLDS = []
    soc_HESS = []
    soc_HESS_OLDS = []
    energy_ch =[]
    energy_dis =[]

    for y in range(project_lifetime):
        for i in range(life_time):
            energy = pv_output[i] - pd_load[i]
            soc_.append(ht.readSOC())
            soc_HESS.append(ht.readSOC())
            ele,sto,eTs = ems.energyStorage(energy)
            energy_ch.append(eTs)
            gridTopower += ele
            ele_cost += ele*grid_price(i)
            stoTopower += sto
            energyTosto += eTs
            energy_dis.append(sto)

    print('HESS')
    print(ele_cost,'grid price')
    print(gridTopower, 'gridTopower')
    print(stoTopower, 'stoTopower')
    print(energyTosto, 'energyTosto')
    ems = HEMS_OLDS(ht=ht,el_power=el_power,fc_power=fc_power,t_start=0,t_end=8766,LIMIT_SUNNY=0.20,LIMIT_CLOUDY=0.25)
    ems.initializa()
    ele_cost = 0
    soc_ = []
    gridTopower = 0
    stoTopower = 0
    energyTosto = 0
    energy_HESS = []
    energy_HESS_OLDS = []
    energy_ch_OLDS = []

    soc_HESS_OLDS = []
    energy_dis_OLDS = []


    for y in range(project_lifetime):
        for i in range(life_time):
            energy = pv_output[i] - pd_load[i]
            soc_.append(ht.readSOC())
            soc_HESS_OLDS.append(ht.readSOC())
            ele, sto, eTs = ems.energyStorage(energy,i)
            gridTopower += ele
            ele_cost += ele * grid_price(i)
            stoTopower += sto
            energyTosto += eTs
            energy_ch_OLDS.append(eTs)
            energy_dis_OLDS.append(sto)

    print('HESS_OLDS')
    print(ele_cost,'grid price')
    print(gridTopower, 'gridTopower')
    print(stoTopower, 'stoTopower')
    print(energyTosto, 'energyTosto')

    plt.plot(list(range(len(soc_HESS[:200]))),soc_HESS[:200],label='HESS')
    plt.plot(list(range(len(soc_HESS_OLDS[:200]))),soc_HESS_OLDS[:200])

    plt.legend()
    plt.show()
    plt.plot(list(range(len(soc_HESS[:200]))),energy_ch[:200],label='HESS')
    plt.plot(list(range(len(soc_HESS[:200]))), energy_ch_OLDS[:200])
    plt.legend()
    plt.show()
    ht.initializa()
    print(ht.max_charge())
    print(sum(energy_ch[:200]))
    plt.plot(list(range(len(energy_dis_OLDS[:200]))), energy_dis[:200], label='HESS')
    plt.plot(list(range(len(energy_dis_OLDS[:200]))), energy_dis_OLDS[:200])
    plt.legend()
    plt.show()



























