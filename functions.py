from gurobipy import *
import re
import math
import numpy as np
import copy
import random


def subtourSelect(tourlist, method='S', measure='number', num=1):

    if method == 'A':
        return tourlist

    elif 'P' not in method:
        if method == 'S':
            tourlist.sort(key=len, reverse=False)

        elif method == 'L':
            tourlist.sort(key=len, reverse=True)

        elif method == 'R':
            random.shuffle(tourlist)

        if measure == 'percentage':
            cut = int(max((len(tourlist) * num), 1))
            output = tourlist[:cut]
        else:
            output = tourlist[:max(num, len(tourlist))]

    else:

        if method == 'P':
            powset = PowerSetWithBound(tourlist, 2 ** num)
            output = powset + tourlist

        elif method == 'POS':
            tourlist.sort(key=len, reverse=False)
            baseSet = tourlist[:min(num, len(tourlist))]
            powset = PowerSet(baseSet)
            output = powset + tourlist

        elif method == 'POL':
            tourlist.sort(key=len, reverse=True)
            baseSet = tourlist[:min(num, len(tourlist))]
            powset = PowerSet(baseSet)
            output = powset + tourlist

        elif method == 'POR':
            random.shuffle(tourlist)
            baseSet = tourlist[:min(num, len(tourlist))]
            powset = PowerSet(baseSet)
            output = powset + tourlist

    return output

def readData(path, nodeNum):
    nodeNum = nodeNum
    cor_X = []
    cor_Y = []

    f = open(path, 'r')
    lines = f.readlines()
    count = 0
    # read the info
    for line in lines:
        count = count + 1
        if (count >= 7 and count < 7 + nodeNum):
            line = line[:-1]
            str = re.split(r" +", line)
            print(str)
            cor_X.append(float(str[1]))
            cor_Y.append(float(str[2]))

    # compute the distance matrix
    disMatrix = [([0] * nodeNum) for p in range(nodeNum)]  # 初始化距离矩阵的维度,防止浅拷贝

    for i in range(0, nodeNum):
        for j in range(0, nodeNum):
            temp = (cor_X[i] - cor_X[j]) ** 2 + (cor_Y[i] - cor_Y[j]) ** 2
            disMatrix[i][j] = (int)(math.sqrt(temp))

    return disMatrix


def printData(disMatrix):
    print("-------cost matrix-------\n")
    for i in range(len(disMatrix)):
        for j in range(len(disMatrix)):

            print("%6.1f" % (disMatrix[i][j]), end=" ")

        print()


def getValue(var_dict, nodeNum):
    x_value = np.zeros([nodeNum + 1, nodeNum + 1])
    for key in var_dict.keys():
        a = key[0]
        b = key[1]
        x_value[a][b] = var_dict[key].x

    return x_value


def getRoute(x_value):

    x = copy.deepcopy(x_value)

    previousPoint = 0

    route_temp = [previousPoint]
    count = 0
    while (len(route_temp) < len(x) and count < len(x)):

        if (x[previousPoint][count] > 0.5):
            previousPoint = count
            route_temp.append(previousPoint)
            count = 0
            continue
        else:
            count += 1
    return route_temp


# given a graph, get the edges of this graph
def findEdges(graph):
    edges = []
    for i in range(0, len(graph)):
        for j in range(0, len(graph)):
            if (graph[i][j] > 0.5):
                edges.append((i, j))

    return edges

# Given a tuplelist of edges, find the shortest subtour
def subtour(graph, nodeNum):
    unvisited = [i for i in range(0, nodeNum + 1)]

    edges = findEdges(graph)
    edges = tuplelist(edges)
    print(edges)


    cyclelist = []

    while unvisited:  # true if list is non-empty

        neighbors = unvisited
        current = neighbors[0]
        thiscycle = [current]
        unvisited.remove(current)

        for i,j in edges.select(current, '*'):
            next = j
            break

        while next:

            current = next
            thiscycle.append(current)

            unvisited.remove(current)
            for c, n in edges.select(current, '*'):
                if n in unvisited:
                    next = n
                else:
                    next = None

        cyclelist.append(thiscycle)

    return cyclelist


def PowerSetWithBound(List, bound):
    # set_size of power set of a set
    # with set_size n is (2**n -1)
    if len(List) < 2:
        return [List]

    set_size = len(List)
    pow_set_size = int(math.pow(2, set_size))
    powerset = []
    print('currentrange', pow_set_size)
    print('currentsample', min(bound, pow_set_size)-1)
    templist = random.sample(range(1, pow_set_size+1), min(bound, pow_set_size))

    # Run from counter 000..0 to 111..
    for n in templist:

        temp = []
        c = 0
        for j in range(0, set_size):

            # Check if jth bit in the
            # counter is set If set then
            # print jth element from set
            if ((n & (1 << j)) > 0):
                temp += List[j]
                c += 1

        if c > 1:
            powerset.append(temp)

    return powerset[1:]

def PowerSet(set):
    # set_size of power set of a set
    # with set_size n is (2**n -1)
    set_size = len(set)
    pow_set_size = (int)(math.pow(2, set_size))
    powerset = []

    # Run from counter 000..0 to 111..1
    for counter in range(0, pow_set_size):
        temp = []
        for j in range(0, set_size):

            # Check if jth bit in the
            # counter is set If set then
            # print jth element from set
            if ((counter & (1 << j)) > 0):
                temp += set[j]
        powerset.append(temp)

    return powerset[1:]