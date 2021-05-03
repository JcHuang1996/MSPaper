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

    global checker, chosen

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

        if checker <= roundnum - 1:

            checker += 1

            tourlist = subtour(x_value, nodeNum)
            if len(tourlist) == 1:
                return

            tours = subtourSelect(tourlist, method, measure, num)

            for tour in tours:
                print('tour = ', tour)
                chosen.append(tour)
                if (len(tour) < nodeNum + 1):
                    print("---add sub tour elimination constraint--")

                    # for i, j in itertools.combinations(tour, 2):
                    # print(i, j)

                    model.cbLazy(quicksum(model._vars[i, j] + model._vars[j, i]
                                          for i, j in itertools.combinations(tour, 2))
                                 <= len(tour) - 1)

checker = 0
chosen = []

starttime = time.time()

nodeNum = 262
path = 'C:/academic/Graduate Paper/code/gil262.txt'
method = 'POS'
num = 1
measure = 'percentage'
roundnum = 1
#measure = 'number'

cost = readData(path, nodeNum)

model = Model('TSP')

# creat decision variables
X = {}
for i in range(nodeNum+1):

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
#model.setParam('TimeLimit', 1000)

model.optimize(subtourelim)

print('constraints are chosen')
print('constraints are ', chosen)
print('GG begins')



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

for tour in chosen:
    if (len(tour) < nodeNum + 1):
        print("---add chosen subtour elimination constraint--")

        # for i, j in itertools.combinations(tour, 2):
        # print(i, j)

        model.addConstr(quicksum(X[i, j] + X[j, i]
                              for i, j in itertools.combinations(tour, 2))
                     <= len(tour) - 1)


model.setParam('MIPFocus', 1)
model.write('model.lp')
model.optimize()

x_value = getValue(X, nodeNum)
route = getRoute(x_value)

print('optimal route:', route)
print('optimal value', model.objVal)

endtime = time.time()
print('time', endtime - starttime)
print('Gap', model.MIPGap)

