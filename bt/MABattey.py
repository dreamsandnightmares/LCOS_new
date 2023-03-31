import matplotlib.pyplot as plt
import numpy as  np
import pandas as pd
import math

from PV.PVModel import PVSystem
import numpy as np
from EL.normalPEM import PEM
from FC.normalFC import PEMFC
from HT.hydrogenStorage import HT
from obj.obj_function import ssr,NPV,NPV_Bess,lcos,lcoe
from price.gridPrice import grid_price
from data_load.data_load import data_load


class LionBattery(object) :

    def __init__(self, Cap_BT, eta_BT_conv, sigma_BT=0.05 / (30 * 24), eta_BT_ch=0.95, eta_BT_dc=0.95,
                 SOC_max=0.80, SOC_min=0.20):
        self.sigma_BT = sigma_BT  # is the battery self-discharge coefficient 5%/month
        self.eta_BT_ch = eta_BT_ch  # is the battery charging efficiencies
        self.eta_BT_dc = eta_BT_dc  # is the battery discharging efficiencies


        self.SOC_t = None
        self.Cap_BT = Cap_BT
        self.delta_t = 1
        self.eta_BT_conv = eta_BT_conv


        self.len_ = len(Cap_BT)

        self.soc_delta = np.zeros(self.len_)
        self.soc_dc = np.zeros(self.len_)
        self.len_ = len(Cap_BT)
        self.SOC_max = np.array([SOC_max]*self.len_)
        self.SOC_min =np.array([SOC_min]*self.len_)


    def initializa(self):
        self.SOC_t =np.array([0.5]*self.len_)

    def StateOfCharge1(self, P_BT_ch, P_BT_dc,):

        self.soc_delta =  P_BT_ch * self.delta_t * self.eta_BT_ch * self.eta_BT_conv / self.Cap_BT - \
                     P_BT_dc * self.delta_t / (self.eta_BT_dc * self.eta_BT_conv * self.Cap_BT)
        return self.soc_delta

    def StateOfCharge(self, P_BT_ch, P_BT_dc, ):
        self.SOC_t = self.SOC_t * (
                    1 - self.sigma_BT) + P_BT_ch * self.delta_t * self.eta_BT_ch * self.eta_BT_conv / self.Cap_BT - \
                     P_BT_dc * self.delta_t / (self.eta_BT_dc * self.eta_BT_conv * self.Cap_BT)


    def self_dc(self,i):
        self.soc_dc  =(1-self.sigma_BT)*self.SOC_t[i]


    def soc(self,i):
        self.self_dc(i)
        self.SOC_t[i] = self.soc_dc+self.soc_delta[i]
        return self.SOC_t





    def max_charge(self):
        '最大充电功率'
        energy = ((self.SOC_max - self.SOC_t * (1 - self.sigma_BT)) * self.Cap_BT / (
                    self.delta_t * self.eta_BT_ch * self.eta_BT_conv))
        return energy



    def max_discharge(self):

        energy = (abs(self.SOC_min - self.SOC_t * (
                    1 - self.sigma_BT)) * self.eta_BT_dc * self.eta_BT_conv * self.Cap_BT) / self.delta_t
        return energy
    def max_discharge_limit(self,soc_limit):

        energy = (abs(soc_limit - self.SOC_t * (
                    1 - self.sigma_BT)) * self.eta_BT_dc * self.eta_BT_conv * self.Cap_BT) / self.delta_t
        return energy
    def readSoc(self):
        self.SOC_t = np.round(self.SOC_t,8)
        return self.SOC_t

    def lifetime(self):
        '暂时用固定寿命去做'

        dod = [50,70,80]
        ctf = [5000,3000,2500]
        LT =0

        for i in range(len(dod)):
            LT +=  2*self.Cap_BT*dod[i]*ctf[i]/len(dod)
        return LT
    def max_soc(self):
        return self.SOC_max

    def min_soc(self):
        return self.SOC_min




