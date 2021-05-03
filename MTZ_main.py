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

nodeNum = 100
path = 'C:/academic/Graduate Paper/code/kroE100.txt'
cost = readData(path, nodeNum)
printData(cost)

model = Model('TSP')

# creat decision variables
X = {}
mu = {}
for i in range(nodeNum + 1):
    mu[i] = model.addVar(lb=0.0
                         , ub=nodeNum  # GRB.INFINITY
                         # , obj = distance_initial
                         , vtype=GRB.CONTINUOUS
                         , name="mu_" + str(i)
                         )

    for j in range(nodeNum + 1):
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
    model.addConstr(lhs == 1, name='visit_' + str(j))

for i in range(0, nodeNum):
    for j in range(1, nodeNum + 1):
        if (i != j):
            model.addConstr(mu[i] - mu[j] + 100 * X[i, j] <= 100 - 1)

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
