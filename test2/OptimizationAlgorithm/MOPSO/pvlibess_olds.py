# encoding: utf-8
from test2.OptimizationAlgorithm.bt.Mopso_res_bt import *


def main():
    particals = 10  # 粒子群的数量
    cycle_ = 50  # 迭代次数
    mesh_div = 10  # 网格等分数量
    thresh = 300  # 外部存档阀值
    project_lifetime = 25
    life_time = 8760
    cost_pv = 5000
    cost_bt = 1900

    Problem = "DTLZ2"
    M = 2
    # Population, Boundary, Coding = P_objective.P_objective("init", Problem, M, particals)
    # # print(Boundary)
    Boundary = np.array([[1500., 2000.], [600., 600.]])
    print(type(Boundary))
    ''
    # Boundary =
    max_ = Boundary[0]
    print(max_, 'max_')
    min_ = Boundary[1]
    print(min_, 'min_')

    # mopso_ = Mopso(particals,max_,min_,thresh,mesh _div) #粒子群实例化
    mopso_ = Mopso_res(particals, max_, min_, thresh, cost_pv=cost_pv, cost_bt=cost_bt,
                       project_lifetime=project_lifetime, life_time=life_time)
    pareto_in, pareto_fitness = mopso_.done(cycle_)  # 经过cycle_轮迭代后，pareto边界粒子

    np.savetxt(r"C:\Users\王晨浩\Desktop\LCOS\test2\OptimizationAlgorithm\pareto_in.txt", pareto_in)  # 保存pareto边界粒子的坐标
    np.savetxt(r"C:\Users\王晨浩\Desktop\LCOS\test2\OptimizationAlgorithm\pareto_fitness.txt",
               pareto_fitness)  # 打印pareto边界粒子的适应值
    print("\n", "pareto边界的坐标保存于：/img_txt/pareto_in.txt")
    print("pareto边界的适应值保存于：/img_txt/pareto_fitness.txt")
    print("\n,迭代结束,over")


if __name__ == "__main__":
    main()