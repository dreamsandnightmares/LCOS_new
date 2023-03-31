import  numpy as np
def sortrows(Matrix, order = "ascend"):
    '对输入的Matrix按照第一列排序，假设第一列相同，则按照第二列排序'
    # 默认先以第一列值大小  对  行  进行排序，若第一列值相同，则按照第二列 值，以此类推,返回排序结果 及对应 索引 （Reason: list.sort() 仅仅返回 排序后的结果， np.argsort() 需要多次 排序，其中、
    #  np.lexsort()的操作对象 等同于 sortcols ，先排以最后一行 对  列  进行排序，然后以倒数第二列，以此类推. np.lexsort((d,c,b,a)来对[a,b,c,d]进行排序、其中 a 为一列向量 ）
    Matrix_temp = Matrix[:, ::-1] #因为np.lexsort() 默认从最后一行 对  列  开始排序，需要将matrix 反向 并 转置
    Matrix_row = Matrix_temp.T
    if order == "ascend":
        rank = np.lexsort(Matrix_row)
    elif order == "descend":
        rank = np.lexsort(-Matrix_row)
    Sorted_Matrix = Matrix[rank,:] # Matrix[rank] 也可以
    return Sorted_Matrix, rank
def NDSort(PopObj,Remain_Num):
    'POP obj  = fitness'
    '判断是否 支配  求取最小值'
    'Remain_Num =  粒子数量'

    N,M = PopObj.shape
    '两个目标函数'


    'M = Remain_Num  是几个目标函数'
    'N 是粒子数'
    '已知信息  现在已经对于第一个目标函数排序了  从小到大'

    FrontNO = np.inf*np.ones((1, N))

    MaxFNO = 0

    '从小到大'
    PopObj, rank = sortrows(PopObj)
    'PopObj  已经排序过了'


    while (np.sum(FrontNO < np.inf) < Remain_Num) :
        b  =np.sum(FrontNO < np.inf )
        MaxFNO += 1

        for i in range(N):
            if FrontNO[0, i] == np.inf:
                Dominated = False
                for j in range(i-1, -1, -1):
                    if FrontNO[0, j] == MaxFNO:
                        m=2
                        while (m <= M) and (PopObj[i, m-1] >= PopObj[j, m-1]):
                            m += 1
                        Dominated = m > M
                        if Dominated or (M == 2):
                            break
                if not Dominated:
                    FrontNO[0,i] = MaxFNO
    # temp=np.loadtxt("temp.txt")
    # print((FrontNO==temp).all())
    front_temp = np.zeros((1,N))
    front_temp[0, rank] = FrontNO
    # FrontNO[0, rank] = FrontNO 不能这么操作，因为 FrontNO值 在 发生改变 ，会影响后续的结果


    return front_temp, MaxFNO

def init_archive(in_,fitness_):

    FrontValue_1_index =NDSort(fitness_, in_.shape[0])[0]==1
    FrontValue_1_index = np.reshape(FrontValue_1_index,(-1,))

    curr_archiving_in=in_[FrontValue_1_index]
    curr_archiving_fit=fitness_[FrontValue_1_index]

    # pareto_c = pareto.Pareto_(in_,fitness_)
    # curr_archiving_in_,curr_archiving_fit_ = pareto_c.pareto()
    return curr_archiving_in,curr_archiving_fit


if __name__ == '__main__':
    # FrontValue_1_index = NDsort.NDSort(fitness_, in_.shape[0])[0] == 1
    #in_.shape[0]  是 粒子个数   =3

    '假设 a 是 fitness'
    # "init", Problem, M, particals
    #
    a = np.random.random((3,2))
    print(a)
    print(np.max(a,axis=0))
    print(np.array([1,1,1]))



    # print(a)
    # print('------')
    # s,r  = sortrows(a)
    # print(s)
    # S,B = NDSort(a,2)
    # print(S,B)
    #
    # print(s)
    # print(r)
    # for i in range(5):
    #     print(i,'i__')
    #     for j in range(i - 1, -1, -1):
    #         print(j)


    # P  = P_DTLZ("init", "DTLZ2", 2, 2)
    # print(P)

    # a = np.random.random((3, 2))
    # b = np.random.random((3,3))
    # i = init_archive(b,a)
