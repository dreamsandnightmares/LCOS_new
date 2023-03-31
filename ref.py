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

                            self.GridToEnergy[i] = energy_
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