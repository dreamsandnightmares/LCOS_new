'储氢系统'
import math

"因为是并网系统  不够就买电 因此不需要满足LPSP 约束"

class HT(object):

        """
                Hydrogen tank
        """

        def __init__(self, Cap_H2, eta_FC, eta_EL, delta_t):
            # 设置LOH max 与min 没有查到相关数据

            self.LOH_t_max = 1
            self.LOH_t_min = 0
            self.Cap_H2 = Cap_H2
            self.eta_FC = eta_FC
            self.delta_t = delta_t
            self.eta_EL = eta_EL
            self.LOH_t = None

        def initializa(self):
            self.LOH_t = 0.1

        def soc(self, P_el, P_fc):
            """
                The output of the ratio between the total amount of energy currently contained
                in the hydrogen tank and its maximum capacity(equation 19)

                Arguments:
                time --
                delta_t -- is the time step (in h)
                eta_EL -- is the electrolyzer efficiencies (already including converter losses).
                Cap_H2 -- (in kWh) is the hydrogen storage tank rated capacity
                eta_FC -- is the fuel cell efficiencies (already including converter losses).
                P_EL_t_1 -- (in kW) corresponds to the electrolyzer operating power (at the DC bus level)
                P_FC_t_1 -- (in kW) corresponds to the fuel cell operating power (at the DC bus level)

                Returns:
                LOH_t --  ratio between the total amount of energy currently contained
                        in the hydrogen tank and its maximum capacity
            """
            # LOH_t_1 = self.LevelOfHydrogen(time - 1)
            # P_EL_t_1 = self.P_EL(time - 1) # (in kW) corresponds to the electrolyzer operating power (at the DC bus level)
            # P_FC_t_1 = self.P_FC(time - 1) # (in kW) corresponds to the fuel cell operating power (at the DC bus level)
            self.LOH_t = self.LOH_t + P_el * self.delta_t * self.eta_EL / self.Cap_H2 - P_fc * self.delta_t / (
                        self.eta_FC * self.Cap_H2)
            return self.LOH_t

        def max_charge(self):
            energy = (self.LOH_t_max - self.LOH_t) * self.Cap_H2 / (self.delta_t * self.eta_EL)
            return energy

        def max_discharge(self):
            energy = abs((self.LOH_t - self.LOH_t_min) * (self.eta_FC * self.Cap_H2) / self.delta_t)
            return energy

        def readSOC(self):
            return self.LOH_t

        def SOC_Max(self):
            return self.LOH_t_max

        def SOC_Min(self):
            return self.LOH_t_min


if __name__ == '__main__':
    ht_cap = 150
    ht = HT(Cap_H2=150,eta_EL=0.86,eta_FC=0.6,delta_t=1)
    ht.initializa()
    print(ht.readSOC())
    print(ht.SOC_Min())
    print(ht.SOC_Max())


    print(ht.max_discharge(),'max_dis')
    print(ht.max_charge())
    print(ht.soc(P_el=156,P_fc=0))





