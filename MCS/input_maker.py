from itertools import product
import csv

Threshold_highList = [19.44, 22.22, 23.61, 25]

Threshold_lowList = [15.28, 16.67, 18.05 , 19.44] 

alphaList = [1, 0.9, 0.8 , 0.7, 0.6, 0.5 ,0.4, 0.3, 0.2, 0.1]

rateList = [1,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1,0]


prodList = list(product(Threshold_highList,Threshold_lowList,alphaList,rateList))

file = open('input.csv', "w", newline='')

columnNames = ["Threshold_high","Threshold_low","Alpha","Rate"]

#print(prodList)

testList = list([[1500,20,0.6,1],[1550,20,0.6,1],[1500,20,1,1],[1500,20,1,0]])

with file:
    write = csv.writer(file)
    write.writerow(columnNames)
    write.writerows(prodList)