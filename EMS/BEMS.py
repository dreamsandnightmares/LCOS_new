from bt.Battey import LionBattery


'没有设置上网电价   后续需要更新'
class BEMS(object):
    def __init__(self, bt: LionBattery):
        self.bt = bt
        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

    def initializa(self):
        self.bt.initializa()
        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

    def energyStorage(self, energy):

        if energy >= 0:
            '充电过程'
            max_charge = self.bt.max_charge()
            if energy <= max_charge:
                self.bt.StateOfCharge(P_BT_ch=energy, P_BT_dc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = energy
            else:

                self.bt.StateOfCharge(P_BT_ch=max_charge, P_BT_dc=0)
                self.GridToEnergy = 0
                self.storageToEnergy = 0
                self.energyToStorage = max_charge
        elif energy < 0:
            '放电过程'
            SOC = self.bt.readSoc()
            if SOC > self.bt.SOC_min:
                max_discharge = self.bt.max_discharge()
                if abs(energy) <= max_discharge:
                    self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=abs(energy))
                    self.GridToEnergy = 0
                    self.storageToEnergy = abs(energy)
                    self.energyToStorage = 0
                else:

                    self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=max_discharge)
                    self.GridToEnergy = abs(energy) - max_discharge
                    self.storageToEnergy = max_discharge
                    self.energyToStorage = 0
            else:
                self.GridToEnergy = abs(energy)
                self.energyToStorage = 0
                self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage


class BEMS_OLDS(object):
    def __init__(self, bt: LionBattery, t_start, t_end, LIMIT_SUNNY, LIMIT_CLOUDY):

        self.bt = bt
        self.GridToEnergy = 0
        self.t_start = t_start
        self.t_end = t_end
        self.LIMIT_SUNNY = LIMIT_SUNNY
        self.LIMIT_CLOUDY = LIMIT_CLOUDY

        self.dis_enable = True
        self.peak_enable = False

    def initializa(self):
        self.bt.initializa()

        self.GridToEnergy = 0
        self.storageToEnergy = 0
        self.energyToStorage = 0

        self.dis_enable = True

    def enable(self, time):
        SOC = self.bt.readSoc()
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
            max_charge = self.bt.max_charge()
            if energy < max_charge:
                self.bt.StateOfCharge(P_BT_ch=energy, P_BT_dc=0)
                self.enable(time)

                self.storageToEnergy = 0
                self.energyToStorage = energy
                self.GridToEnergy = 0
            else:
                self.bt.StateOfCharge(P_BT_ch=max_charge, P_BT_dc=0)
                self.enable(time)

                self.energyToStorage = max_charge
                self.storageToEnergy = 0
                self.GridToEnergy = 0

        else:
            '放电过程'
            "所有energy 要取绝对值"
            energy = abs(energy)
            if self.t_start <= time <= self.t_end:
                SOC = self.bt.readSoc()
                if SOC > self.LIMIT_CLOUDY:
                    self.if_peak(time)
                    if self.peak_enable:
                        max_discharge = self.bt.max_discharge_limit(self.LIMIT_CLOUDY)
                        if energy <= max_discharge:
                            self.bt.StateOfCharge(P_BT_dc=energy, P_BT_ch=0)
                            self.enable(time)

                            self.energyToStorage = 0
                            self.storageToEnergy = energy
                            self.GridToEnergy = 0
                        else:
                            self.bt.StateOfCharge(P_BT_dc=max_discharge, P_BT_ch=0)
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
                SOC = self.bt.readSoc()
                if SOC > self.LIMIT_SUNNY:
                    if self.dis_enable == True:
                        max_discharge = self.bt.max_discharge_limit(self.LIMIT_SUNNY)
                        if energy <= max_discharge:
                            self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=energy)

                            self.energyToStorage = 0
                            self.GridToEnergy = 0
                            self.storageToEnergy = energy

                            self.enable(time)
                        else:
                            self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=max_discharge)
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

            #
            # if SOC > self.bt.SOC_min:
            #     if self.dis_enable == True:
            #         max_discharge = self.bt.max_discharge_limit(self.LIMIT_CLOUDY)
            #         if energy <= max_discharge:
            #             self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=energy)
            #
            #             self.energyToStorage = 0
            #             self.GridToEnergy = 0
            #             self.storageToEnergy = energy
            #
            #             self.enable(time)
            #         else:
            #             self.bt.StateOfCharge(P_BT_ch=0, P_BT_dc=max_discharge)
            #             self.enable(time)
            #
            #             self.energyToStorage = 0
            #             self.GridToEnergy = energy - max_discharge
            #             self.storageToEnergy = max_discharge
            #
            #     else:
            #         if self.t_start <= time <= self.t_end:
            #             '定义 t_start - t_end 为光伏为0的时间'
            #             '储能系统仅在 电价贵的时候放电'
            #             self.if_peak(time)
            #             if self.peak_enable:
            #                 max_discharge = self.bt.max_discharge()
            #                 if energy <= max_discharge:
            #                     self.bt.StateOfCharge(P_BT_dc=energy, P_BT_ch=0)
            #                     self.enable(time)
            #
            #                     self.energyToStorage = 0
            #                     self.storageToEnergy = energy
            #                     self.GridToEnergy = 0
            #                 else:
            #                     self.bt.StateOfCharge(P_BT_dc=max_discharge, P_BT_ch=0)
            #                     self.enable(time)
            #
            #                     self.energyToStorage = 0
            #                     self.GridToEnergy = energy - max_discharge
            #                     self.storageToEnergy = max_discharge
            #
            #
            #             else:
            #                 self.GridToEnergy = energy
            #                 self.energyToStorage = 0
            #                 self.storageToEnergy = 0
            #
            # else:
            #     self.GridToEnergy = abs(energy)
            #     self.energyToStorage = 0
            #     self.storageToEnergy = 0
        return self.GridToEnergy, self.storageToEnergy, self.energyToStorage





















