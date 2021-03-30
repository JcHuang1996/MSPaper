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

starttime = time.time()

nodeNum = 107

path = 'C:/academic/Graduate Paper/code/pr107.txt'
cost = readData(path, nodeNum)
printData(cost)

model = Model('TSP')

# creat decision variables
X = {}
mu = {}
for i in range(nodeNum + 1):
    for j in range(nodeNum + 1):
        if (i != j):
            X[i, j] = model.addVar(vtype=GRB.BINARY
                                   , name='x_' + str(i) + '_' + str(j)
                                   )

for i in range(nodeNum + 1):
    for j in range(nodeNum + 1):
        if (i != j):
            mu[i, j] = model.addVar(lb=0.0
                         , ub=nodeNum + 2  # GRB.INFINITY
                         # , obj = distance_initial
                         , vtype=GRB.CONTINUOUS
                         , name="mu_" + str(i)
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
    model.addConstr(lhs == 1, name='visit_' + str(j))

# add constraints 9.8
for j in range(1, nodeNum + 1):
    model.addConstr(mu[0, j] == nodeNum * X[0, j], name = 'Const 9.8' + str(j))

# add constraints 9.9
for i in range(0, nodeNum + 1):
    for j in range(0, nodeNum + 1):
        if (i != j):
            model.addConstr(mu[i, j] <= nodeNum * X[i, j], name='Const 9.9'+str(i)+'to'+str(j))


# add constraints 9.10
for j in range(1, nodeNum + 1):
    lhs = LinExpr(0)
    for i in range(nodeNum + 1):
        if (i != j):
            lhs.addTerms(1, mu[i, j])
            lhs.addTerms(-1, mu[j, i])
    model.addConstr(lhs == 1, name='Const 9.10 ' + str(j))

model.setParam('TimeLimit', 1000)
model.write('model.lp')
model.optimize()

x_value = getValue(X, nodeNum)
route = getRoute(x_value)

print('optimal route:', route)
print('optimal value', model.objVal)

endtime = time.time()
print('time', endtime - starttime)
print('Gap', model.MIPGap)
