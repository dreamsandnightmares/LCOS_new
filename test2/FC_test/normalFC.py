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
        return i*self.func(i)*self.A/1000

    def max_power(self):
        i = self.max_i()
        # print(i,'电流密度')
        v =self.func(i)
        # print(v,'电压')
        return  i*v*self.A/1000



if __name__ == '__main__':
    Pem = PEMFC()
    '测试  功率与电流的关系'
    '假设电流密度为1'
    P_list = []
    I_sol_list = []
    error =[]
    I  = np.arange(0.01,1.49,0.0001)
    for i in I:
        u  = Pem.func(i)

        P = u*i

        P_list.append(P)
        i_sol = Pem.readi(P)
        error.append(i-i_sol)

        I_sol_list.append(i_sol)
    print(max(error),min(error))

    '求解 电流'



