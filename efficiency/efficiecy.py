
'''
'锂电池、铅酸电池'

电解槽： ALK PEM SOEC
储氢系统：储氢罐
发电侧：燃料电池 氢燃气轮机

'''
import math
import matplotlib.pyplot as plt


if __name__ == '__main__':
    sto_hours = 1000

    eff_li_up = []
    eff_li_down = []

    eff_pb_up = []
    eff_pb_dwon = []

    eff_h2_alk_fc_up = []
    eff_h2_alk_fc_down = []

    eff_h2_alk_hq_up = []
    eff_h2_alk_hq_down = []

    eff_h2_pem_fc_up =[]
    eff_h2_pem_fc_down = []


    eff_h2_pem_hq_up =[]
    eff_h2_pem_hq_down = []

    eff_h2_soec_fc_up =[]
    eff_h2_soec_fc_down = []

    eff_h2_soec_hq_up = []
    eff_h2_soec_hq_down = []
    eff_li = []
    eff_pb =[]
    eff_h2 = []

    for i in range(8760):
        eff_pb_dwon.append(60*math.pow(1-0.000125,i))
        eff_pb_up.append(77*math.pow(1-0.00004166667,i))
        eff_h2_alk_fc_down.append(46)
        eff_h2_alk_fc_up.append(52)








    for i in range(len(eff_pb_dwon)):
        eff_pb.append ((eff_pb_up[i] - eff_pb_dwon[i])/2 +eff_pb_dwon[i])
        eff_h2.append(( eff_h2_alk_fc_up[i] - eff_h2_alk_fc_down[i] )/2+eff_h2_alk_fc_down[i])

    dist = list(range(len(eff_pb)))
    print(math.pow(1-0.0125,100))
    plt.plot(dist,eff_pb,label ='li_battery')

    plt.plot(dist,eff_h2,label ='H2_storage')
    plt.legend()
    plt.fill_between(dist,eff_pb_up,eff_pb_dwon,color=(229/256, 204/256, 249/256), alpha=0.9)
    plt.fill_between(dist,eff_h2_alk_fc_up,eff_h2_alk_fc_down,color = (204/256, 236/256, 223/256),alpha =0.9)
    plt.ylabel('efficiency')
    plt.xlabel('hours [h]')
    # plt.title("电池储能与储氢储能在不同时间尺度下综合效率变化")
    plt.savefig('电池储能与储氢储能在不同时间尺度下综合效率变化')
    plt.show()


