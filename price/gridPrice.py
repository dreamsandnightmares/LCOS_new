from data_load.data_load import data_load


def grid_price(time):
    price = 0
    if 5 <= int(time/(30*24))<9 or int(time/(30*24)) ==10 :
        if 12<=time%24 <14:
            price =2
            pass
        elif 8<= time%24<12 or 14<=time%24<15 or 18<=time%24<21:
            price =1.3
            pass
        elif 6<= time%24<8 or 15<=time%24<18 or 21<=time%24<22:
            price =0.6
            pass
        elif 0<= time%24<6 or 22<=time%24<24:
            price =0.3
    elif int(time/(30*24))==9 :
        if 8<=time%24 <15 or 18<=time%24 <21 :
            price= 1.3
        elif 6<=time%24 <8 or 15<=time%24 <18 or 21<=time%24 <22:
            price = 0.6
        elif 0<=time%24 <6 or 22<=time%24 <24:
            price = 0.3
    elif int(time/(30*24)) ==12 or int(time/30/24)==1:
        if  19<=time%24 <21:
            price = 2
        elif  8<=time%24 <11 or 18<=time%24 <19:
            price = 1.3
        elif   6<=time%24 <8 or 11<=time%24 <18 or  21<=time%24 <22:
            price = 0.6
        elif 0<=time%24 <6 or 22<=time%24 <24:
            price = 0.3
    else:
        if 8 <= time % 24 < 11 or   18<=time%24 <19:
            price = 1.3
        elif 6 <= time % 24 < 8 or   11<=time%24 <18 or 21<=time%24 <22 :
            price = 0.6
        else:
            price = 0.3
    return price

def grid_price1(time):
    pass




if __name__ == '__main__':
    pd_load, pd_price, pd_wea_wind, pd_wea_G_dir, pd_wea_G_diff, pd_wea_T, pd_wea_G_hor = data_load()
    grid_cost =0
    load_all = 0
    for i in range(8670):
        GridPrice = grid_price(i)
        load_all+=pd_load[i]
        grid_cost+=pd_load[i]*GridPrice
    print(grid_cost*25)
    print(load_all*25)

