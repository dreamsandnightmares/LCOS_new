import math
import numpy as np


import pandas as pd
import matplotlib.pyplot as plt
from PV.PVModel import PVSystem
from data_load.data_load import data_load
class PEMFC(object):

    def __init__(self):
        self.A =200
        pass

    def func(self, x):
        if 0<=x<=1.5:

            U =-0.675*math.pow(x,5)+2.8231*math.pow(x,4)-4.3617*math.pow(x,3)+3.0737*math.pow(x,2)-1.1195*x+0.9879
        else:
            print('FC current density error')
            U = np.inf

        return U
    def H2_cost(self,i,n):
        m  =1.05*math.pow(10,-8)*(i*n)
        return m

    def equation(self,x):
        return -0.675*math.pow(x,6)+2.8231*math.pow(x,5)-4.3617*math.pow(x,4)+3.0737*math.pow(x,3)-1.1195*math.pow(x,2)+0.9879*x

    def readi(self,y,a=0, b=1.5, tol=1e-6):
        fa = self.equation(a) - y
        fb = self.equation(b) - y
        if fa * fb > 0:
            return None
        while abs(b - a) > tol:
            c = (a + b) / 2
            fc = self.equation(c) - y
            if fc == 0:
                return c
            elif fa * fc < 0:
                b = c
                fb = fc
            else:
                a = c
                fa = fc
        return (a + b) / 2


    def max_i(self):
        return 1.5
    def power(self,i):
        if i >1.5:
            i = 1.499999
        else:
            pass

        return i*self.func(i)*self.A/1000

    def max_power(self):
        i = self.max_i()
        # print(i,'电流密度')
        v =self.func(i)
        # print(v,'电压')
        return  i*v*self.A/1000





if __name__ == '__main__':
    Pem = PEMFC()
    # U_=[]
    # i_ =[]
    # i_list = np.arange(0.001, 1.5, 0.01)
    # for i in (i_list):
    #     i_.append(i)
    #     # print(i)
    #     U_.append(Pem.func(i))
    # plt.plot(i_,U_)
    # plt.ylim(0,2.5)
    # print(Pem.func(1.5))
    # i = Pem.readi(0.84)
    # print(i)
    # print(Pem.max_power(),'max_power')
    pv_cap = 250
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()
    pv =PVSystem(pv_cap,pd_wea_T=pd_wea_T,pd_wea_G_dir=pd_wea_G_dir,pd_wea_G_diff=pd_wea_G_diff,pd_wea_G_hor=pd_wea_G_hor)
    fc_energy  =[]
    for i  in range(8760):
        energy = pd_load[i]  - pv.PVpower(i)
        if energy >=0:
               energy = energy/150
               fc_energy.append(energy)

    print()
    # print(max(fc_energy),'max')
    # print(min(fc_energy),'min')
    # for i in range (len(fc_energy)):
    #     print(Pem.readi(fc_energy[i]))



