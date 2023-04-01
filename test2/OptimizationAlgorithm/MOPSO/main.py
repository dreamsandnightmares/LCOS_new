#encoding: utf-8
from Mopso import *
from public import  P_objective
from test2.OptimizationAlgorithm.bt.Mopso_res_bt import *

 
def main():

    particals = 2 #粒子群的数量
    cycle_ = 100 #迭代次数
    mesh_div = 10 #网格等分数量
    thresh = 300#外部存档阀值

    pv_cap = 3000
    bt_cap = 3000
    project_lifetime = 25
    life_time = 8760
    cost_pv = 5000
    cost_bt = 1900





    Problem = "DTLZ2"
    M = 2
    Population, Boundary, Coding = P_objective.P_objective("init", Problem, M, particals)
    # print(Boundary)
    # Boundary = np.array([[5000.,5000.],[1000.,1000.]])
    print(type(Boundary))
    ''
    # Boundary =
    max_ = Boundary[0]

    min_ = Boundary[1]



    mopso_ = Mopso(particals,max_,min_,thresh,mesh_div) #粒子群实例化
    # mopso_ = Mopso_res(particals,max_,min_,thresh,pv_cap=pv_cap,bt_cap=bt_cap,cost_pv=cost_pv,cost_bt=cost_bt,
    #                   project_lifetime=project_lifetime,life_time=life_time)
    pareto_in,pareto_fitness = mopso_.done(cycle_) #经过cycle_轮迭代后，pareto边界粒子
    np.savetxt("./img_txt/pareto_in.txt",pareto_in)#保存pareto边界粒子的坐标
    np.savetxt("./img_txt/pareto_fitness.txt",pareto_fitness) #打印pareto边界粒子的适应值
    print ("\n","pareto边界的坐标保存于：/img_txt/pareto_in.txt")
    print ("pareto边界的适应值保存于：/img_txt/pareto_fitness.txt")
    print ("\n,迭代结束,over")


 
if __name__ == "__main__":
    main()
