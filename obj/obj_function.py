import math


def ssr(P_grid,P_load):
    return ((P_grid/P_load))

def NPV(r_0,r_bess,cost_bt,cost_h2,cost_el,cost_fc,li_cap,h2_cap,el_cap
        ,fc_cap,cost_om,project_time):
    npv =0
    cost_cap_bt = cost_bt*li_cap
    cost_cap_h2 =cost_h2*h2_cap
    cost_cap_fc = cost_fc*fc_cap
    cost_cap_el = cost_el*el_cap
    cost_cap = cost_cap_el+cost_cap_bt+cost_cap_fc+cost_cap_h2
    for i in range(project_time):

        if i ==11:
            cost_rep = 0.60*cost_cap_bt

            npv += ((r_0-r_bess) - cost_om - cost_rep) /math.pow((1+0.05),i) - cost_cap
        elif i == 5:
            cost_rep = cost_fc*0.775
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        elif i ==15:
            cost_rep = cost_fc * 0.55+cost_el*0.6
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        elif i == 20:
            cost_rep = cost_fc * 0.325
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        elif i == 25:
            cost_rep = cost_fc * 0.1
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap
        else:
            cost_rep = 0
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i) - cost_cap

    return npv

def NPV_Bess(r_0,r_bess,cost_pv,cost_bt,li_cap,pv_cap,project_time):
    npv =0
    cost_cap_bt = cost_bt*li_cap
    cost_cap_pv = pv_cap*cost_pv
    cost_om = cost_cap_bt*0.005+cost_cap_pv*0.01

    # print(cost_om,'om')
    #
    # print(r_0,'r_init')
    # print(r_bess,'r_bess')

    cost_cap = cost_cap_bt+cost_cap_pv
    # print(cost_cap,'cap')
    for i in range(project_time):

        if i ==11:
            cost_rep = 0.60*cost_cap_bt

            npv += ((r_0-r_bess) - cost_om - cost_rep) /math.pow((1+0.05),i)
            # print(((r_0-r_bess) - cost_om - cost_rep) /math.pow((1+0.05),i),'rep')

        else:
            cost_rep = 0
            npv += ((r_0 - r_bess) - cost_om - cost_rep) / math.pow((1 + 0.05), i)
            # print(((r_0-r_bess) - cost_om - cost_rep) /math.pow((1+0.05),i),'not rep')
    # print(npv)
    npv = npv  - cost_cap

    return npv

def lcos(cost_pv,cost_bt,li_cap,pv_cap,project_time,ele,wout):
    cost_cap_bt = cost_bt * li_cap
    cost_cap_pv = pv_cap * cost_pv
    cost_om = cost_cap_bt * 0.005 + cost_cap_pv * 0.01
    at =0
    wout_all =0
    cost_cap = cost_cap_bt + cost_cap_pv

    for i in range(project_time):
        if  i ==11:
            cost_rep = 0.60 * cost_cap_bt

            at += (cost_om+cost_rep+0.3*ele)/math.pow((1+0.05),i)

            wout_all = wout/math.pow((1+0.05),i)
    return (cost_cap+at)/wout_all

def lcoe(cost_pv,cost_bt,li_cap,pv_cap,project_time,energy):
    cost_cap_bt = cost_bt * li_cap
    cost_cap_pv = pv_cap * cost_pv
    cost_om = cost_cap_bt * 0.005 +19*pv_cap
    d = 0.05
    down = 0
    cost_om_all = 0
    cost_rep = 0.60 * cost_cap_bt
    cost_cap = cost_cap_bt + cost_cap_pv


    for i in range(project_time):
        cost_om_all +=cost_om/(math.pow((1+d),i))

        down +=(energy/(math.pow((1+d),i)))
    lcoe_ = (cost_cap+cost_om_all+cost_rep-0.5*cost_cap)/down
    return lcoe_












