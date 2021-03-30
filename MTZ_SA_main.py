from gurobipy import *
import re
import math
import numpy as np
import copy
import time

from functions import readData
from functions import printData
from functions import getValue
from functions import getRoute
from functions import subtour
from functions import subtourSelect

def subtourelim(model, where):
    if (where == GRB.Callback.MIPSOL):
        # make a list of edges selected in the solution
        #print('model._vars', model._vars)
        #         vals = model.cbGetSolution(model._vars)
        x_value = np.zeros([nodeNum + 1, nodeNum + 1])
        for m in model.getVars():
            if (m.varName.startswith('x')):
                #                 print(var[i].varName)
                #                 print(var[i].varName.split('_'))
                a = (int)(m.varName.split('_')[1])
                b = (int)(m.varName.split('_')[2])
                x_value[a][b] = model.cbGetSolution(m)
        #print("solution = ", x_value)

        tourlist = subtour(x_value, nodeNum)
        if len(tourlist) == 1:
            return

        nonzlist = [t for t in tourlist if 0 not in t]
        tours = subtourSelect(nonzlist, method, measure, num)

        for tour in tours:
            print('tour = ', tour)
            if (len(tour) < nodeNum + 1):
                print("---add sub tour elimination constraint--")

                for i, j in itertools.combinations(tour, 2):
                    print(i, j)

                    model.cbLazy(mu[i] - mu[j] + nodeNum * X[i, j] <= nodeNum - 1)
                    model.cbLazy(mu[j] - mu[i] + nodeNum * X[j, i] <= nodeNum - 1)

                #for p1 in range(0, len(tour)):
                #    if p1 > 0:
                #        p2 = p1 - 1
                #        i, j = tour[p1], tour[p2]
                #        model.cbLazy(mu[i] - mu[j] + nodeNum * X[i, j] <= nodeNum - 1)
                #        model.cbLazy(mu[j] - mu[i] + nodeNum * X[j, i] <= nodeNum - 1)
                #    else:
                #        p2 = -1
                #        i, j = tour[p1], tour[p2]
                #        model.cbLazy(mu[i] - mu[j] + nodeNum * X[i, j] <= nodeNum - 1)
                #        model.cbLazy(mu[j] - mu[i] + nodeNum * X[j, i] <= nodeNum - 1)

starttime = time.time()

nodeNum = 48
path = 'C:/academic/Graduate Paper/code/att48.txt'
cost = readData(path, nodeNum)
printData(cost)

method = 'S'
num = 0.5
#measure = 'number'
measure = 'percentage'

model = Model('TSP')

# creat decision variables
X = {}
mu = {}

for i in range(nodeNum+1):
    mu[i] = model.addVar(lb=0.0
                         , ub= nodeNum+2  # GRB.INFINITY
                         # , obj = distance_initial
                         , vtype=GRB.CONTINUOUS
                         , name="mu_" + str(i)
                         )

    for j in range(nodeNum+1):
        if (i != j):
            X[i, j] = model.addVar(vtype=GRB.BINARY
                                   , name='x_' + str(i) + '_' + str(j)
                                   )

# set objective function
obj = LinExpr(0)
for key in X.keys():
    i = key[0]
    j = key[1]
    if (i < nodeNum and j < nodeNum):
        obj.addTerms(cost[key[0]][key[1]], X[key])
    elif (i == nodeNum):
        obj.addTerms(cost[0][key[1]], X[key])
    elif (j == nodeNum):
        obj.addTerms(cost[key[0]][0], X[key])

model.setObjective(obj, GRB.MINIMIZE)

# add constraints 1
for j in range(0, nodeNum + 1):
    lhs = LinExpr(0)
    for i in range(0, nodeNum + 1):
        if (i != j):
            lhs.addTerms(1, X[i, j])
    model.addConstr(lhs == 1, name='visit_' + str(j))

# add constraints 2
for i in range(0, nodeNum + 1):
    lhs = LinExpr(0)
    for j in range(0, nodeNum + 1):
        if (i != j):
            lhs.addTerms(1, X[i, j])
    model.addConstr(lhs == 1, name='from_' + str(j))

model.addConstr(X[nodeNum, 0] == 1, name = 'visit_' + str(0) + ',' + str(nodeNum))
model.addConstr(X[0 ,nodeNum] == 0, name = 'visit_' + str(0) + ',' + str(nodeNum))

# set lazy constraints
model._vars = X
model.Params.lazyConstraints = 1
model.setParam('TimeLimit', 1000)

model.optimize(subtourelim)
# subProblem.optimize()
x_value = getValue(X, nodeNum)
route = getRoute(x_value)

print('optimal route:', route)
print('optimal value', model.objVal)

endtime = time.time()
print('time', endtime - starttime)
print('Gap', model.MIPGap)