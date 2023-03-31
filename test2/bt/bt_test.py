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
        # self.len_ = len(Cap_BT)
        self.SOC_max = SOC_max
        self.SOC_min =SOC_min
        self.soc_delta = 0
        self.soc_dc = 0
        # self.len_ = len(Cap_BT)

    def initializa(self):
        self.SOC_t =0.5

    def StateOfCharge1(self, P_BT_ch, P_BT_dc,):

        self.soc_delta =  P_BT_ch * self.delta_t * self.eta_BT_ch * self.eta_BT_conv / self.Cap_BT - \
                     P_BT_dc * self.delta_t / (self.eta_BT_dc * self.eta_BT_conv * self.Cap_BT)
        return self.soc_delta

    def StateOfCharge(self, P_BT_ch, P_BT_dc, ):
        self.SOC_t = self.SOC_t * (
                    1 - self.sigma_BT) + P_BT_ch * self.delta_t * self.eta_BT_ch * self.eta_BT_conv / self.Cap_BT - \
                     P_BT_dc * self.delta_t / (self.eta_BT_dc * self.eta_BT_conv * self.Cap_BT)


    def self_dc(self):
        self.soc_dc  =(1-self.sigma_BT)*self.SOC_t


    def soc(self):
        self.self_dc()

        self.SOC_t = self.soc_dc+self.soc_delta
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

def device_init(in_: np.array):
        pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()

        pv_cap = in_[:, 0]
        print(pv_cap, 'PV_CAP')
        pv = PVSystem(pv_cap, pd_wea_T=pd_wea_T, pd_wea_G_dir=pd_wea_G_dir, pd_wea_G_diff=pd_wea_G_diff,
                      pd_wea_G_hor=pd_wea_G_hor)

        bt_cap = in_[:, 1]
        print(bt_cap, 'BT_CAP')
        bt = LionBattery(bt_cap, eta_BT_conv=0.98)
        bt.initializa()
        pv_output = []
        R_init = 0
        for i in range(8760):
            pv_output.append(pv.PVpower(i))
            R_init += pd_load[i] * grid_price(i)

        return pv, bt, pd_load, pd_price, pv_output, R_init
if __name__ == '__main__':
    project_lifetime = 25
    life_time = 8760
    in_ = np.array([[3000, 2000]])
    print(in_)
    pv, bt, pd_load, pd_price, pv_output, R_init = device_init(in_)
    print(pv_output[2])


    a = 0
    a = np.append(a,0)
    print(a)
    print(bt.SOC_min)
    print(bt.StateOfCharge(P_BT_dc=1,P_BT_ch=0))
    print(bt.SOC_t)
    "分开计算"
    # bt.initializa()
    # b = bt.StateOfCharge1(P_BT_dc=0,P_BT_ch=0)
    # print(bt.readSoc())
    # print(b)
    # # c= bt.self_dc()
    #
    #
    # a = bt.soc()
    # print(a)