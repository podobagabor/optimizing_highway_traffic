from itertools import product
import csv

maxCapacityList = [1683,1783,1883,1983,2083,2183]

speedReduceList = [11.11,16.67,19.44,22.22 ]

alphaList = [1,0.9,0.8,0.7]

rateList = [1,0.9,0.8,0.7,0.6,0.5]

reducedSpeedInflowList = [16.67,19.44,22.22,25]

prodList = list(product(maxCapacityList,speedReduceList,alphaList,rateList,reducedSpeedInflowList))

file = open('input.csv', "w", newline='')

columnNames = ["MaxCapacity","Speed","Alpha","Rate","ReducedSpeedInflow"]

#print(prodList)

testList = list([[1500,20,0.6,1],[1550,20,0.6,1],[1500,20,1,1],[1500,20,1,0]])

with file:
    write = csv.writer(file)
    write.writerow(columnNames)
    write.writerows(prodList)