from bt.MABattey import LionBattery
from HT.ma_hydrogenStorage  import HT
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from PV.PVModel import PVSystem
import matplotlib.pyplot as plt
import math
from price.gridPrice import grid_price
from data_load.data_load import data_load
import numpy as np
class HybridESS(object):
    def __init__(self, bt: LionBattery,ht:HT,el_power,fc_power):
        self.bt = bt
        self.ht = ht
        self.len = len(bt.readSoc())
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)

        self.el_power= el_power
        self.fc_power= fc_power

    def initializa(self):
        self.bt.initializa()
        self.ht.initializa()
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)

    def energyStorage(self, energy):
        for i in range(self.len):

            P_BT_dc = np.zeros([self.bt.len_])
            P_BT_ch = np.zeros([self.bt.len_])
            P_fc = np.zeros([self.ht.len_])
            P_el = np.zeros([self.ht.len_])

            if energy[i] >= 0:
                '充电过程'
                max_charge = self.bt.max_charge()[i]
                if energy[i] <= max_charge:
                    P_BT_ch[i] = energy[i]
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)

                    self.GridToEnergy[i] = 0
                    self.storageToEnergy[i] = 0
                    self.energyToStorage[i] = energy[i]

                else:
                    P_BT_ch[i] = max_charge
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)
                    self.GridToEnergy[i] = 0
                    self.storageToEnergy[i] = 0
                    self.energyToStorage[i] = max_charge

                    energyToStorage = max_charge
                    energy_ = energy[i] -max_charge

                    max_charge = min(self.ht.max_charge()[i],self.el_power[i])
                    if energy_ <= max_charge:
                        P_el[i] = energy[i]
                        self.ht.SOC(P_el=P_el,P_fc=P_fc)

                        self.GridToEnergy[i] = 0
                        self.storageToEnergy[i] = 0
                        self.energyToStorage[i] = energy[i]+energyToStorage

                    else:
                        P_el[i] = max_charge
                        self.ht.SOC(P_el=P_el,P_fc=P_fc)
                        self.GridToEnergy[i] = 0
                        self.storageToEnergy[i] = 0
                        self.energyToStorage[i] = max_charge+energyToStorage

            elif energy[i] < 0:
                P_BT_dc = np.zeros([self.bt.len_])
                P_BT_ch = np.zeros([self.bt.len_])
                P_fc = np.zeros([self.ht.len_])
                P_el = np.zeros([self.ht.len_])

                '放电过程'
                SOC = self.bt.readSoc()[i]
                if SOC > self.bt.SOC_min[i]:
                    max_discharge = self.bt.max_discharge()[i]

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

                        energy_ = abs(energy[i]) - max_discharge
                        stoToenergy=max_discharge

                        SOC = self.ht.readSOC()[i]
                        if SOC > self.ht.SOC_Min()[i]:
                            max_discharge = min(self.ht.max_discharge()[i],self.fc_power[i])
                            if energy_ <= max_discharge:
                                P_fc[i] = energy_
                                self.ht.SOC(P_el=P_el,P_fc=P_fc)
                                self.GridToEnergy[i] = 0
                                self.storageToEnergy[i] = energy_ +stoToenergy
                                self.energyToStorage[i] = 0
                            else:
                                P_fc[i] = max_discharge
                                self.ht.SOC(P_el=P_el,P_fc=P_fc)
                                self.GridToEnergy[i] = energy_ - max_discharge
                                self.storageToEnergy[i] = max_discharge+stoToenergy
                                self.energyToStorage[i] = 0

                        else:

                            self.GridToEnergy[i] = abs(energy[i]) -stoToenergy
                            self.energyToStorage[i] = 0
                            self.storageToEnergy[i] = stoToenergy


                else:
                        P_fc = np.zeros([self.ht.len_])
                        P_el = np.zeros([self.ht.len_])
                        SOC = self.ht.readSOC()[i]
                        if SOC > self.ht.SOC_Min()[i]:
                            max_discharge = min(self.ht.max_discharge()[i],self.fc_power[i])
                            if abs(energy[i]) <= max_discharge:

                                P_fc[i] = abs(energy[i])
                                self.ht.SOC(P_el=P_el, P_fc=P_fc)
                                self.GridToEnergy[i] = 0
                                self.storageToEnergy[i] = abs(energy[i])
                                self.energyToStorage[i] = 0
                            else:
                                P_fc[i] = max_discharge
                                self.ht.SOC(P_el=P_el, P_fc=P_fc)

                                self.GridToEnergy[i] = abs(energy[i]) - max_discharge
                                self.storageToEnergy[i] = max_discharge
                                self.energyToStorage[i] = 0

                        else:
                            self.GridToEnergy[i] = abs(energy[i])
                            self.energyToStorage[i] = 0
                            self.storageToEnergy[i] = 0

        return  self.GridToEnergy, self.storageToEnergy, self.energyToStorage


class HybridESS_OLDS(object):
    def __init__(self, bt: LionBattery,ht:HT,el_power,fc_power,t_start, t_end, LIMIT_SUNNY, LIMIT_CLOUDY):
        self.ht = ht
        self.bt = bt
        self.el_power= el_power
        self.fc_power= fc_power


        self.t_start = t_start
        self.t_end = t_end
        self.LIMIT_SUNNY = LIMIT_SUNNY
        self.LIMIT_CLOUDY = LIMIT_CLOUDY
        self.peak_enable = False

        self.len = len(bt.readSoc())
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)
        self.dis_enable_bt = np.array([True] * self.len)
        self.dis_enable_ht = np.array([True] * self.len)



    def initializa(self):
        self.ht.initializa()
        self.bt.initializa()

        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)

        self.dis_enable_bt = np.array([True] * self.len)
        self.dis_enable_ht = np.array([True] * self.len)
    def enable_bt(self, time,i):
        SOC = self.bt.readSoc()[i]

        if self.t_start <= time <= self.t_end:
            if SOC > self.LIMIT_CLOUDY:
                self.dis_enable_bt[i] = True
            else:
                self.dis_enable_bt[i] = False
        else:
            if SOC > self.LIMIT_SUNNY:
                self.dis_enable_bt[i] = True
            else:
                self.dis_enable_bt[i] = False

    def enable_ht(self, time,i):
        SOC = self.ht.readSOC()[i]
        if self.t_start <= time <= self.t_end:
            if SOC > self.LIMIT_CLOUDY:
                self.dis_enable_ht[i] = True
            else:
                self.dis_enable_ht[i]= False
        else:
            if SOC > self.LIMIT_SUNNY:
                self.dis_enable_ht[i] = True
            else:
                self.dis_enable_ht[i] = False

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
            P_fc = np.zeros([self.ht.len_])
            P_el = np.zeros([self.ht.len_])

            if energy[i] >= 0:
                "充电过程"
                max_charge = self.bt.max_charge()[i]
                if energy[i] < max_charge:
                    P_BT_ch[i] = energy[i]
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)
                    self.enable_bt(time, i)

                    self.storageToEnergy[i] = 0
                    self.energyToStorage[i] = energy[i]
                    self.GridToEnergy[i] = 0
                else:
                    P_BT_ch[i] = max_charge
                    self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                    self.bt.soc(i)

                    self.enable_bt(time,i)

                    energyToStorage = max_charge
                    energy_ = energy[i] - max_charge

                    max_charge = min(self.ht.max_charge()[i],self.el_power[i])

                    if energy_ <= max_charge:
                        P_el[i] = energy_
                        self.ht.SOC(P_el=P_el, P_fc=P_fc)
                        self.enable_ht(time, i)

                        self.GridToEnergy[i] = 0
                        self.storageToEnergy[i] = 0
                        self.energyToStorage[i] = energy_ + energyToStorage
                    else:
                        P_el[i] = max_charge
                        self.ht.SOC(P_el=P_el, P_fc=P_fc)
                        self.enable_ht(time, i)
                        self.GridToEnergy[i] = 0
                        self.storageToEnergy[i] = 0
                        self.energyToStorage[i] = max_charge + energyToStorage

            else:
                P_BT_dc = np.zeros([self.bt.len_])
                P_BT_ch = np.zeros([self.bt.len_])
                P_fc = np.zeros([self.ht.len_])
                P_el = np.zeros([self.ht.len_])

                '放电过程'
                "所有energy 要取绝对值"

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
                                self.enable_bt(time, i)

                                self.energyToStorage[i] = 0
                                self.storageToEnergy[i] = abs(energy[i])
                                self.GridToEnergy[i] = 0
                            else:
                                P_BT_dc[i] = max_discharge
                                self.bt.StateOfCharge1(P_BT_dc=P_BT_dc, P_BT_ch=P_BT_ch)
                                self.bt.soc(i)
                                self.enable_bt(time,i)

                                energy_ = abs(energy[i]) - max_discharge
                                stoToenergy = max_discharge

                                SOC = self.ht.readSOC()[i]
                                if SOC > self.LIMIT_CLOUDY:
                                    if self.peak_enable:
                                        max_discharge = min(self.ht.max_discharge()[i],self.fc_power[i])
                                        if energy_ <= max_discharge:
                                            P_fc[i] = energy_
                                            self.ht.SOC(P_el=P_el, P_fc=P_fc)
                                            self.enable_ht(time, i)
                                            self.GridToEnergy[i] = 0
                                            self.storageToEnergy[i] = energy_ + stoToenergy
                                            self.energyToStorage[i] = 0
                                        else:
                                            P_fc[i] = max_discharge
                                            self.ht.SOC(P_el=P_el,P_fc=P_fc)
                                            self.enable_ht(time,i)

                                            self.GridToEnergy[i] = energy_ - max_discharge
                                            self.storageToEnergy[i] = max_discharge + stoToenergy
                                            self.energyToStorage[i] = 0
                                else:
                                    self.GridToEnergy[i] = energy_
                                    self.energyToStorage[i] = 0
                                    self.storageToEnergy[i] = stoToenergy
                        else:
                            self.GridToEnergy[i] = abs(energy[i])
                            self.energyToStorage[i] = 0
                            self.storageToEnergy[i] = 0

                    else:
                        SOC = self.ht.readSOC()[i]
                        if SOC > self.LIMIT_CLOUDY:
                            self.if_peak(time)
                            if self.peak_enable:
                                max_discharge = min(self.ht.max_discharge_limit(self.LIMIT_CLOUDY)[i], self.fc_power[i])
                                if abs(energy[i]) <= max_discharge:
                                    P_fc[i] = abs(energy[i])

                                    self.ht.SOC(P_el=P_el, P_fc=P_fc)



                                    self.energyToStorage[i] = 0
                                    self.storageToEnergy[i] = abs(energy[i])
                                    self.GridToEnergy[i] = 0
                                    self.enable_ht(time,i)
                                else:
                                    P_fc[i] = max_discharge
                                    self.ht.SOC(P_el=P_el, P_fc=P_fc)
                                    self.enable_ht(time,i)

                                    self.energyToStorage[i] = 0
                                    self.GridToEnergy[i] = abs(energy[i]) - max_discharge
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
                    SOC = self.bt.readSoc()[i]
                    if SOC > self.LIMIT_SUNNY:

                        max_discharge = self.bt.max_discharge_limit(self.LIMIT_SUNNY)[i]

                        if abs(energy[i]) <= max_discharge:
                                P_BT_dc[i] = abs(energy[i])
                                self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                                self.bt.soc(i)
                                self.enable_bt(time,i)
                                self.GridToEnergy[i] = 0
                                self.storageToEnergy[i] = abs(energy[i])
                                self.energyToStorage[i] = 0
                                self.enable_ht(time,i)
                        else:
                                P_BT_dc[i] = max_discharge
                                self.bt.StateOfCharge1(P_BT_ch=P_BT_ch, P_BT_dc=P_BT_dc)
                                self.bt.soc(i)
                                self.enable_bt(time,i)

                                energy_ = abs(energy[i]) - max_discharge
                                stoToenergy = max_discharge

                                SOC = self.ht.readSOC()[i]
                                if SOC > self.LIMIT_SUNNY:

                                        max_discharge = min(self.ht.max_discharge_limit(self.LIMIT_SUNNY)[i],self.fc_power[i])
                                        if energy_ <= max_discharge:
                                            P_fc[i] = energy_
                                            self.ht.SOC(P_el=P_el, P_fc=P_fc)
                                            self.enable_ht(time,i)
                                            self.GridToEnergy[i] = 0
                                            self.storageToEnergy[i] = energy_ + stoToenergy
                                            self.energyToStorage[i] = 0


                                        else:

                                            P_fc[i] = max_discharge
                                            self.ht.SOC(P_el=P_el, P_fc=P_fc)
                                            self.enable_ht(time,i)

                                            self.GridToEnergy[i] = energy_ - max_discharge
                                            self.storageToEnergy[i] = max_discharge + stoToenergy
                                            self.energyToStorage[i] = 0

                                else:
                                    self.GridToEnergy[i] = energy_
                                    self.energyToStorage[i] = 0
                                    self.storageToEnergy[i] = stoToenergy
                    else:
                        P_fc = np.zeros([self.ht.len_])
                        P_el = np.zeros([self.ht.len_])
                        SOC = self.ht.readSOC()[i]
                        if SOC > self.LIMIT_SUNNY:

                                max_discharge = min(self.ht.max_discharge()[i],self.fc_power[i])
                                if abs(energy[i]) <= max_discharge:
                                    P_fc[i] = abs(energy[i])
                                    self.ht.SOC(P_el=P_el, P_fc=P_fc)

                                    self.GridToEnergy[i] = 0
                                    self.storageToEnergy[i] = abs(energy[i])
                                    self.energyToStorage[i] = 0

                                    self.enable_ht(time,i)
                                else:
                                    P_fc[i] = max_discharge
                                    self.ht.SOC(P_el=P_el, P_fc=P_fc)
                                    self.enable_ht(time,i)

                                    self.GridToEnergy[i] = abs(energy[i]) - max_discharge
                                    self.storageToEnergy[i] = max_discharge
                                    self.energyToStorage[i] = 0
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

    bt_cap = in_[:, 1]
    print(bt_cap, 'BT_CAP')
    bt = LionBattery(bt_cap, eta_BT_conv=0.98)
    bt.initializa()

    el_power = in_[:,2]
    print(el_power,'el_power')

    fc_power= in_[:,3]
    ht_cap  = in_[:,4]
    print(ht_cap,'ht_cap')
    ht = HT(Cap_H2=ht_cap)
    ht.initializa()
    print(fc_power,'fc_power')
    pv_output =[]
    R_init = 0
    for i in range(8760):
        pv_output.append(pv.PVpower(i))
        R_init +=pd_load[i]*grid_price(i)



    return pv,bt,el_power,fc_power,ht,pd_load,pd_price,pv_output,R_init
def energy_management(project_lifetime:int,life_time:int,bt:LionBattery,ht:HT,el:np.array,fc:np.array,pv_output:np.array,pd_load):
    res_output = pv_output


    ems  =HybridESS (bt=bt,ht=ht,el_power=el,fc_power=fc)

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
            energy = np.round(energy,8)
            # print(energy,'energy')
            # print(energy.shape)
            soc_.append(ht.readSOC())
            soc_BESS.append(ht.readSOC())
            ele, sto, eTs = ems.energyStorage(energy)
            gridTopower += ele
            stoTopower += sto
            energyTosto += eTs
            energy_BESS.append(ele)
            ele_cost += ele * grid_price(i)
            ele_all += pd_load[i]
            energy_sto.append(eTs)
            energy_sto_dis.append(sto)
    print(ht.LOH_t)
    a = bt.readSoc()
    print(a,'soc')
    return gridTopower,stoTopower,energyTosto,ele_cost,ele_all
def energy_management_OLDS(project_lifetime:int,life_time:int,bt,ht:HT,el:np.array,fc:np.array,pv_output:np.array,pd_load,
                           t_start,t_end,limit_cloudy,limit_sunny,):
    res_output = pv_output


    ems  = HybridESS_OLDS(bt=bt,ht=ht,el_power=el,fc_power=fc,t_start=t_start,t_end=t_end,LIMIT_CLOUDY=limit_cloudy,LIMIT_SUNNY=limit_sunny)
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
            energy = np.round(energy,8)
            # print(energy,'energy')
            # print(energy.shape)
            soc_.append(ht.readSOC())
            soc_BESS.append(ht.readSOC())
            ele, sto, eTs = ems.energyStorage(energy,i)
            gridTopower += ele
            stoTopower += sto
            energyTosto += eTs
            energy_BESS.append(ele)
            ele_cost += ele * grid_price(i)
            ele_all += pd_load[i]
            energy_sto.append(eTs)
            energy_sto_dis.append(sto)
    return gridTopower,stoTopower,energyTosto,ele_cost,ele_all


if __name__ == '__main__':
    project_lifetime = 25
    life_time = 8760
    ' PV BT EL FC HT'
    in_ = np.array([[450, 600,300, 350, 1000], [450, 600,300, 350, 1000]])
    pv, bt, el_power, fc_power, ht, pd_load, pd_price, pv_output, R_init = device_init(in_)
    gridTopower, stoTopower, energyTosto, ele_cost, ele_all = energy_management(project_lifetime=project_lifetime,
                                                                                     life_time=life_time,bt=bt, ht=ht,
                                                                                     pv_output=pv_output,
                                                                                     pd_load=pd_load,el=el_power,fc=fc_power)
    # gridTopower, stoTopower, energyTosto, ele_cost, ele_all = energy_management_OLDS(project_lifetime=project_lifetime,
    #                                                                                  life_time=life_time,bt=bt, ht=ht,
    #                                                                                  pv_output=pv_output,
    #                                                                                  pd_load=pd_load,el=el_power,fc=fc_power,t_start=0,t_end=1000,
    #                                                                                  limit_sunny=0.2,limit_cloudy=0.25)
    print(ele_cost)
    print(gridTopower,'gridTopower')
    print(stoTopower,'stoTopower')
    print(energyTosto,'energyTosto')




