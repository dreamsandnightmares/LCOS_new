from test2.bt.bt_test import LionBattery
from HT.hydrogenStorage import HT
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from PV.PVModel import PVSystem
import matplotlib.pyplot as plt
import math
from price.gridPrice import grid_price
from data_load.data_load import data_load
class HybridESS(object):
    def __init__(self, bt: LionBattery,ht:HT,el_power,fc_power):
        self.bt = bt
        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0
        self.ht = ht
        self.el = el_power
        self.fc = fc_power

    def initializa(self):
        self.bt.initializa()
        self.ht.initializa()
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
                energyToStorage = max_charge
                self.energyToStorage = max_charge

                energy = energy -max_charge
                max_charge = min(self.ht.max_charge(), self.el)
                if energy <= max_charge:
                    self.ht.soc(P_el=energy, P_fc=0)
                    self.GridToEnergy = 0
                    self.storageToEnergy = 0
                    self.energyToStorage = energy+energyToStorage
                else:
                    self.ht.soc(P_el=max_charge, P_fc=0)
                    self.GridToEnergy = 0
                    self.storageToEnergy = 0
                    self.energyToStorage = max_charge+energyToStorage
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
                    energy = abs(energy) - max_discharge
                    stoToenergy=max_discharge
                    SOC = self.ht.readSOC()
                    if SOC > self.ht.SOC_Min():
                        max_discharge = min(self.ht.max_discharge(), self.fc)
                        if abs(energy) <= max_discharge:
                            self.ht.soc(P_el=0, P_fc=abs(energy))
                            self.GridToEnergy = 0
                            self.storageToEnergy = abs(energy)+stoToenergy
                            self.energyToStorage = 0
                        else:
                            self.ht.soc(P_el=0, P_fc=abs(max_discharge))
                            self.GridToEnergy = abs(energy) - max_discharge
                            self.storageToEnergy = max_discharge+stoToenergy
                            self.energyToStorage = 0
                    else:
                        self.GridToEnergy = abs(energy)
                        self.energyToStorage = 0
                        self.storageToEnergy = stoToenergy


            else:
                    SOC = self.ht.readSOC()
                    if SOC > self.ht.SOC_Min():
                        max_discharge = min(self.ht.max_discharge(), self.fc)
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

        return  self.GridToEnergy, self.storageToEnergy, self.energyToStorage






class HybridESS_OLDS(object):
    def __init__(self, bt: LionBattery,ht:HT,el_power,fc_power,t_start, t_end, LIMIT_SUNNY, LIMIT_CLOUDY):
        self.ht = ht
        self.bt = bt
        self.el = el_power
        self.fc = fc_power

        self.GridToEnergy = 0
        self.t_start = t_start
        self.t_end = t_end
        self.LIMIT_SUNNY = LIMIT_SUNNY
        self.LIMIT_CLOUDY = LIMIT_CLOUDY

        self.dis_enable_bt = True
        self.dis_enable_ht = True
        self.peak_enable = False

    def initializa(self):
        self.ht.initializa()
        self.bt.initializa()

        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

        self.dis_enable_bt = True
        self.dis_enable_ht = True
    def enable_bt(self, time):
        SOC = self.bt.readSoc()
        if self.t_start <= time <= self.t_end:
            if SOC > self.LIMIT_CLOUDY:
                self.dis_enable_bt = True
            else:
                self.dis_enable_bt = False
        else:
            if SOC > self.LIMIT_SUNNY:
                self.dis_enable_bt = True
            else:
                self.dis_enable_bt = False

    def enable_ht(self, time):
        SOC = self.ht.readSOC()
        if self.t_start <= time <= self.t_end:
            if SOC > self.LIMIT_CLOUDY:
                self.dis_enable_ht = True
            else:
                self.dis_enable_ht= False
        else:
            if SOC > self.LIMIT_SUNNY:
                self.dis_enable_ht = True
            else:
                self.dis_enable_ht = False

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
                self.enable_bt(time)

                self.storageToEnergy = 0
                self.energyToStorage = energy
                self.GridToEnergy = 0
            else:
                self.bt.StateOfCharge(P_BT_ch=max_charge, P_BT_dc=0)
                self.enable_bt(time)
                energy_bt=max_charge
                energy = energy -max_charge
                max_charge = min(self.ht.max_charge(), self.el)
                if energy < max_charge:
                    self.ht.soc(P_el=energy, P_fc=0)
                    self.enable_ht(time)

                    self.storageToEnergy = 0
                    self.energyToStorage = energy+energy_bt
                    self.GridToEnergy = 0
                else:
                    self.ht.soc(P_el=max_charge, P_fc=0)
                    self.enable_ht(time)
                    self.storageToEnergy = 0
                    self.energyToStorage = max_charge + energy_bt
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
                            self.enable_bt(time)

                            self.energyToStorage = 0
                            self.storageToEnergy = energy
                            self.GridToEnergy = 0
                        else:
                            self.bt.StateOfCharge(P_BT_dc=max_discharge, P_BT_ch=0)
                            self.enable_bt(time)
                            energy_bt = max_discharge

                            energy = energy - max_discharge
                            SOC = self.ht.readSOC()
                            if SOC > self.LIMIT_CLOUDY:
                                if self.peak_enable:
                                    max_discharge = min(self.ht.max_discharge_limit(self.LIMIT_CLOUDY), self.fc)
                                    if energy <= max_discharge:
                                        self.ht.soc(P_el=0, P_fc=abs(energy))
                                        self.enable_ht(time)
                                        self.energyToStorage = 0
                                        self.storageToEnergy = energy+energy_bt
                                        self.GridToEnergy = 0
                                    else:
                                        self.ht.soc(P_el=0, P_fc=max_discharge)
                                        self.enable_ht(time)
                                        self.energyToStorage = 0
                                        self.storageToEnergy = max_discharge + energy_bt
                                        self.GridToEnergy = energy - max_discharge
                            else:
                                self.energyToStorage = 0
                                self.storageToEnergy = energy_bt
                                self.GridToEnergy = energy
                    else:
                                self.energyToStorage = 0
                                self.storageToEnergy = 0
                                self.GridToEnergy = energy

                else:
                    SOC = self.ht.readSOC()
                    if SOC > self.LIMIT_CLOUDY:
                        if self.peak_enable:
                            max_discharge = min(self.ht.max_discharge_limit(self.LIMIT_CLOUDY), self.fc)
                            if energy <= max_discharge:
                                self.ht.soc(P_el=0, P_fc=abs(energy))
                                self.enable_ht(time)
                                self.energyToStorage = 0
                                self.storageToEnergy = energy
                                self.GridToEnergy = 0
                            else:
                                self.ht.soc(P_el=0, P_fc=max_discharge)
                                self.enable_ht(time)
                                self.energyToStorage = 0
                                self.storageToEnergy = max_discharge
                                self.GridToEnergy = energy - max_discharge
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

                        max_discharge = self.bt.max_discharge_limit(self.LIMIT_SUNNY)
                        if energy <= max_discharge:
                            self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=energy)

                            self.energyToStorage = 0
                            self.GridToEnergy = 0
                            self.storageToEnergy = energy
                            self.enable_bt(time)
                        else:
                            self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=max_discharge)
                            self.enable_bt(time)

                            energy_bt =max_discharge

                            energy = energy - max_discharge

                            SOC = self.ht.readSOC()
                            if SOC > self.LIMIT_SUNNY:

                                    max_discharge = min(self.ht.max_discharge_limit(self.LIMIT_SUNNY), self.fc)
                                    if energy <= max_discharge:
                                        self.ht.soc(P_el=0, P_fc=abs(energy))

                                        self.energyToStorage = 0
                                        self.GridToEnergy = 0
                                        self.storageToEnergy = energy+energy_bt

                                        self.enable_ht(time)
                                    else:

                                        self.ht.soc(P_el=0, P_fc=max_discharge)
                                        self.enable_ht(time)

                                        self.energyToStorage = 0
                                        self.GridToEnergy = energy - max_discharge
                                        self.storageToEnergy = max_discharge+energy_bt

                            else:
                                self.GridToEnergy = energy
                                self.energyToStorage = 0
                                self.storageToEnergy = energy_bt
                else:
                    SOC = self.ht.readSOC()
                    if SOC > self.LIMIT_SUNNY:

                            max_discharge = min(self.ht.max_discharge_limit(self.LIMIT_SUNNY), self.fc)
                            if energy <= max_discharge:
                                self.ht.soc(P_el=0, P_fc=abs(energy))

                                self.energyToStorage = 0
                                self.GridToEnergy = 0
                                self.storageToEnergy = energy

                                self.enable_ht(time)
                            else:
                                self.ht.soc(P_el=0, P_fc=max_discharge)
                                self.enable_ht(time)

                                self.energyToStorage = 0
                                self.GridToEnergy = energy - max_discharge
                                self.storageToEnergy = max_discharge

                    else:
                        self.GridToEnergy = energy
                        self.energyToStorage = 0
                        self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage

def device_init():
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

    pv_cap  = 650
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

    ht_cap = 2000
    ht = HT(ht_cap,eta_FC=0.6,eta_EL=0.86,delta_t=1)
    ht.initializa()
    pv_output =[]
    R_init = 0
    for i in range(8760):
        pv_output.append(pv.PVpower(i))
        R_init +=pd_load[i]*grid_price(i)



    return pv,bt,el,el_n,fc,fc_n,ht,pd_load,pd_price,pv_output,R_init


if __name__ == '__main__':
    pv, bt, el, el_n, fc, fc_n, ht, pd_load, pd_price, pv_output, R_init = device_init()
    project_lifetime = 25
    life_time = 8760
    ems = HybridESS(bt=bt,ht=ht,el_power=230,fc_power=240
                    )
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
    energy_ch = []
    energy_dis = []
    energy_diff =[]
    energy_sys =[]
    for y in range(project_lifetime):
        for i in range(life_time):
            energy = pv_output[i] - pd_load[i]
            energy_diff.append(energy)
            soc_.append(ht.readSOC())
            soc_HESS.append(ht.readSOC())
            ele, sto, eTs = ems.energyStorage(energy)
            energy_sys.append(abs(ele)+abs(sto)+abs(eTs))
            energy_ch.append(eTs)
            gridTopower += ele
            ele_cost += ele * grid_price(i)
            stoTopower += sto
            energyTosto += eTs
            energy_dis.append(sto)
    test1 = []
    for i in range(len(energy_diff)):
        test1.append(abs(energy_diff[i]) -abs(energy_sys[i]))
    print(max(test1),min(test1))
    print(max((energy_diff)))
    plt.plot(list(range(len(energy_diff[:300]))),energy_diff[:300])
    plt.plot(list(range(len(energy_diff[:300]))),test1[:300])
    plt.show()

    print('HybridESS')
    print(ele_cost, 'grid price')
    print(stoTopower, 'energy sto')
    print(energyTosto, 'sto discharge')
    print(gridTopower, 'gridTopower')
    #
    ems = HybridESS_OLDS(bt=bt, ht=ht, el_power=230, fc_power=240,t_start=0,t_end=1000,LIMIT_SUNNY=0.20,LIMIT_CLOUDY=0.25)
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
    energy_ch = []
    energy_dis = []
    energy_diff =[]
    energy_sys =[]
    for y in range(project_lifetime):
        for i in range(life_time):
            energy = pv_output[i] - pd_load[i]
            soc_.append(ht.readSOC())
            soc_HESS.append(ht.readSOC())
            ele, sto, eTs = ems.energyStorage(energy,i)
            energy_ch.append(eTs)
            gridTopower += ele
            ele_cost += ele * grid_price(i)
            stoTopower += sto
            energyTosto += eTs
            energy_dis.append(sto)
            energy_diff.append((energy))
            energy_sys.append(abs(ele)+abs(sto)+abs(eTs))

    print('HybridESS_OLDS')
    print(ele_cost, 'grid price')
    print(stoTopower, 'energy sto')
    print(energyTosto, 'sto discharge')
    print(gridTopower, 'gridTopower')
    #
    test = []
    for i in range(len(energy_diff)):
        test.append(abs(energy_diff[i]) -abs(energy_sys[i]))
    print(max(test),min(test))
    print(max((energy_diff)))
    plt.plot(list(range(len(energy_diff[:300]))),energy_diff[:300])
    plt.plot(list(range(len(energy_diff[:300]))),test[:300])
    plt.show()



