'储氢系统'
import math
import numpy as  np


"因为是并网系统  不够就买电 因此不需要满足LPSP 约束"


class HT(object):
    """
            Hydrogen tank
    """

    def __init__(self, Cap_H2, eta_FC, eta_EL, delta_t):
        # 设置LOH max 与min 没有查到相关数据

        self.Cap_H2 = Cap_H2
        self.eta_FC = eta_FC

        self.eta_EL = eta_EL
        self.delta_t = 1
        self.LOH_t = None
        self.len_ = len(Cap_H2)
        self.LOH_t_max = np.array([1]*self.len_)
        self.LOH_t_min =np.array([0.1]*self.len_)
        self.loh_delta = np.zeros(self.len_)
        self.loh_dc = np.zeros(self.len_)

    def initializa(self):
        self.LOH_t = np.array([0.2]*self.len_)

    def SOC(self, P_el, P_fc):

        self.LOH_t = self.LOH_t + P_el * self.delta_t * self.eta_EL / self.Cap_H2 - P_fc * self.delta_t / (
                self.eta_FC * self.Cap_H2)
        return self.LOH_t

    def max_charge(self):
        energy = (self.LOH_t_max - self.LOH_t) * self.Cap_H2 / (self.delta_t * self.eta_EL)
        return energy

    def max_discharge(self):
        energy = abs((self.LOH_t - self.LOH_t_min) * (self.eta_FC * self.Cap_H2) / self.delta_t)
        return energy
    def max_discharge_limit(self,limit):
        energy = abs((self.LOH_t - limit) * (self.eta_FC * self.Cap_H2) / self.delta_t)
        return energy

    def readSOC(self):
        return self.LOH_t

    def SOC_Max(self):
        return self.LOH_t_max

    def SOC_Min(self):
        return self.LOH_t_min



if __name__ == '__main__':
    ht_cap = np.array([150,200])


    ht = HT(Cap_H2= ht_cap,eta_EL=0.86,eta_FC=0.6,delta_t=1)
    ht.initializa()
    print(ht.readSOC())
    print(ht.SOC_Min())
    print(ht.SOC_Max())
    P_EL  =np.zeros(len(ht_cap))
    P_fc = np.zeros(len(ht_cap))

    ht.SOC(P_el=P_EL,P_fc=P_fc)
    print(ht.readSOC())












