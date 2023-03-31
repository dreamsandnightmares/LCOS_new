import math
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
from PV.PVModel import PVSystem
from data_load.data_load import data_load

'A  = 150 CM2'
class PEM(object):

    def __init__(self):
        self.path = '/home/wch/Desktop/LCOS/EL/1.xlsx'
        self.A =150

    def i_V(self):
        pd_data = pd.read_excel(self.path)
        i = pd_data["电流密度/ (A cm-2)"]
        V = pd_data['电压 / V']
        # print(i)
        # print(pd_data)
        plt.plot(i,V)
        plt.ylim(0,2.5)
        # plt.show()

    def func(self,x):
        if 0<=x<=2:
            U = 0.0876*math.pow(x,3)-0.2941*math.pow(x,2)+0.5128*x+1.4673
        else:
            print('FC current density error')

            U = np.inf

        return U
    def H2_gen(self,i,n):
        m  =1.05*math.pow(10,-8)*(i*n)
        return m
    def readi(self,y,a=0, b=2,  tol=1e-6):
        'P  =0.0876*X**4 -0.2941*X**3 +0.5128*X**2+1.4673X'
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

    def equation(slef,x):
        return 0.0876 * x ** 4 - 0.2941 * x ** 3 + 0.5128 * x ** 2 + 1.4373*x

    def max_i(self):
        return 2
    def max_power(self):
        i = self.max_i()
        # print(i,'电流密度')
        v = self.func(i)
        # print(v,'电压')
        max_power = i*self.A*v/1000
        return max_power
    def power(self,i):
        return i*self.func(i)*self.A/1000

    def LHV(self,i):


        return 1.25/self.func(i)








if __name__ == '__main__':
    Pem = PEM()
    '测试  功率与电流的关系'
    '假设电流密度为1'
    P_list = []
    I_sol_list = []
    error = []
    I = np.arange(0.01, 1.5, 0.0001)
    for i in I:
        u = Pem.func(i)

        P = u * i

        P_list.append(P)
        i_sol = Pem.readi(P)
        error.append(i - i_sol)

        I_sol_list.append(i_sol)
    print(max(error),min(error))

