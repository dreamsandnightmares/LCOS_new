class HEMS(object):
    def __init__(self,ht:HT,el_power,fc_power):
        self.ht =ht
        self.len =len(ht.LOH_t)
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)
        self.el_power= el_power
        self.fc_power= fc_power


    def initializa(self):
        self.ht.initializa()
        self.GridToEnergy = np.zeros(self.len)
        self.storageToEnergy = np.zeros(self.len)
        self.energyToStorage = np.zeros(self.len)

    def energyStorage(self, energy):
       for i in range(len(energy)):
           P_fc = np.zeros([self.ht.len_]  )
           P_el = np.zeros([self.ht.len_]  )

           if energy[i] >= 0:

                # print(energy[i])

                '充电过程'
                max_charge = min(self.ht.max_charge()[i],self.el_power[i])
                if energy[i] <= max_charge:
                    P_el[i] = energy[i]
                    self.ht.SOC(P_el=P_el,P_fc=P_fc)


                    self.GridToEnergy[i] = 0
                    self.storageToEnergy[i] =0
                    self.energyToStorage[i] =energy[i]
                else:
                    P_el[i] = max_charge
                    self.ht.SOC(P_el=P_el,P_fc=P_fc)
                    self.GridToEnergy[i] = 0
                    self.storageToEnergy[i] = 0
                    self.energyToStorage [i]=max_charge
           elif energy[i] < 0:
                P_fc = np.zeros([self.ht.len_])
                P_el = np.zeros([self.ht.len_])
                '放电过程'
                SOC = self.ht.readSOC()[i]
                # print(SOC,'SOC')
                # print(self.bt.SOC_min)
                if SOC > self.ht.SOC_Min()[i]:
                    max_discharge = min(self.ht.max_discharge()[i],self.fc_power[i])
                    # print(type(max_discharge))
                    # print(max_discharge[i,:])

                    if abs(energy[i]) <= max_discharge:

                        P_fc[i] = abs(energy[i])
                        self.ht.SOC(P_el=P_el,P_fc=P_fc)
                        self.GridToEnergy[i] = 0
                        self.storageToEnergy[i] = abs(energy[i])
                        self.energyToStorage[i] = 0
                    else:
                        P_fc[i] = max_discharge
                        self.ht.SOC(P_el=P_el,P_fc=P_fc)

                        self.GridToEnergy[i] =abs(energy[i]) - max_discharge
                        self.storageToEnergy[i] =  max_discharge
                        self.energyToStorage[i] =  0
                else:
                    P_fc = np.zeros([self.ht.len_])
                    P_el = np.zeros([self.ht.len_])
                    self.ht.SOC(P_el=P_el,P_fc=P_fc)
                    self.GridToEnergy[i] =  abs(energy[i])
                    self.energyToStorage[i] = 0
                    self.storageToEnergy[i] = 0


       return self.GridToEnergy, self.storageToEnergy, self.energyToStorage