import pandas as pd
import matplotlib.pyplot as plt

class PEM(object):

    def __init__(self):
        self.path = '/home/wch/Desktop/LCOS/EL/2.xlsx'
        self.path1 = '/home/wch/Desktop/LCOS/EL/1.xlsx'

    def i_V(self):
        pd_data = pd.read_excel(self.path)
        print(pd_data)
        i = pd_data["电流密度/(A cm-2)"]
        V = pd_data['电压/(V)']
        pd_data = pd.read_excel(self.path1)
        i1 = pd_data["电流密度/ (A cm-2)"]
        V1 = pd_data['电压 / V']

        # print(i)
        # print(pd_data)
        plt.plot(i,V,label ='best')
        plt.legend()
        plt.plot(i1,V1)
        plt.ylim(0,2.5)
        plt.show()




if __name__ == '__main__':
    Pem = PEM()
    Pem.i_V()