from HT.hydrogenStorage import HT
from EL.normalPEM import PEM
from FC.normalFC import PEMFC

class HEMS(object):
    def __init__(self,ht:HT,el_power,fc_power):
        self.ht =ht
        self.GridToEnergy =0
        self.el = el_power
        self.fc =fc_power

    def initializa(self):
        '初始化'
        self.ht.initializa()
        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0
    def energyStorage(self,energy):
        if energy >= 0:
            '充电过程'
            max_charge = min(self.ht.max_charge(),self.el)
            if energy <= max_charge:
                self.ht.soc(P_el=energy,P_fc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = energy
            else:
                self.ht.soc(P_el=max_charge,P_fc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = max_charge
        elif energy < 0:
            '放电过程'
            SOC = self.ht.readSOC()
            if SOC > self.ht.SOC_Min():
                max_discharge =min(self.ht.max_discharge(),self.fc)
                if abs(energy) <= max_discharge:
                    self.ht.soc(P_el=0, P_fc=abs(energy))
                    self.GridToEnergy = 0
                    self.storageToEnergy = abs(energy)
                    self.energyToStorage = 0
                else:
                    self.ht.soc(P_el=0, P_fc=abs(max_discharge))
                    self.GridToEnergy = abs(energy) - max_discharge
                    self.storageToEnergy = max_discharge
                    self.energyToStorage = 0
            else:
                self.GridToEnergy = abs(energy)
                self.energyToStorage = 0
                self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage





class HEMS_OLDS(object):
    def __init__(self, ht:HT,el_power,fc_power, t_start, t_end, LIMIT_SUNNY, LIMIT_CLOUDY):

        self.ht = ht
        self.GridToEnergy = 0
        self.t_start = t_start
        self.t_end = t_end
        self.LIMIT_SUNNY = LIMIT_SUNNY
        self.LIMIT_CLOUDY = LIMIT_CLOUDY
        self.el =el_power
        self.fc =fc_power

        self.dis_enable = True
        self.peak_enable = False

    def initializa(self):
        self.ht.initializa()

        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

        self.dis_enable = True

    def enable(self, time):
        SOC = self.ht.readSOC()
        if self.t_start <= time <= self.t_end:
            if SOC > self.LIMIT_CLOUDY:
                self.dis_enable = True
            else:
                self.dis_enable = False
        else:
            if SOC > self.LIMIT_SUNNY:
                self.dis_enable = True
            else:
                self.dis_enable = False


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
        if energy >= 0:
            "充电过程"
            max_charge = min(self.ht.max_charge(), self.el)
            if energy < max_charge:
                self.ht.soc(P_el=energy, P_fc=0)
                self.enable(time)

                self.storageToEnergy = 0
                self.energyToStorage = energy
                self.GridToEnergy = 0
            else:
                self.ht.soc(P_el=max_charge,P_fc=0)
                self.enable(time)

                self.energyToStorage = max_charge
                self.storageToEnergy = 0
                self.GridToEnergy = 0

        else:
            '放电过程'
            "所有energy 要取绝对值"
            energy = abs(energy)
            if self.t_start <= time <= self.t_end:
                SOC = self.ht.readSOC()
                if SOC > self.LIMIT_CLOUDY:
                    self.if_peak(time)
                    if self.peak_enable:
                        max_discharge =min(self.ht.max_discharge_limit(self.LIMIT_CLOUDY),self.fc)
                        if energy <= max_discharge:
                            self.ht.soc(P_el=0, P_fc=abs(energy))
                            self.enable(time)
                            self.energyToStorage = 0
                            self.storageToEnergy = energy
                            self.GridToEnergy = 0
                        else:
                            self.ht.soc(P_el=0, P_fc=max_discharge)
                            self.enable(time)

                            self.energyToStorage = 0
                            self.GridToEnergy = energy - max_discharge
                            self.storageToEnergy = max_discharge
                    else:
                            self.GridToEnergy = energy
                            self.energyToStorage = 0
                            self.storageToEnergy = 0
                else:
                    self.GridToEnergy = energy
                    self.energyToStorage = 0
                    self.storageToEnergy = 0

            else:
                SOC = self.ht.readSOC()
                if SOC > self.LIMIT_SUNNY:
                    if self.dis_enable == True:
                        max_discharge =min(self.ht.max_discharge_limit(self.LIMIT_SUNNY),self.fc)
                        if energy <= max_discharge:
                            self.ht.soc(P_el=0, P_fc=abs(energy))

                            self.energyToStorage = 0
                            self.GridToEnergy = 0
                            self.storageToEnergy = energy

                            self.enable(time)
                        else:
                            self.ht.soc(P_el=0, P_fc=max_discharge)
                            self.enable(time)

                            self.energyToStorage = 0
                            self.GridToEnergy = energy - max_discharge
                            self.storageToEnergy = max_discharge
                    else:
                        self.GridToEnergy = energy
                        self.energyToStorage = 0
                        self.storageToEnergy = 0
                else:
                    self.GridToEnergy = energy
                    self.energyToStorage = 0
                    self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage



















