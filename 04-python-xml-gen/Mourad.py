# Introduction to Python

# Why Python?

## Powerful...

# Use in VSeA?

## Tooling, testing signal and bus values.

# Exercises

## Exercise 1
x = "HelloWorld!"
print(len(x))

## Exercise 2
myList = [3, 5, 8, 9]

sum = 0
for i in myList:
    sum += i
print(sum)

## Exercise 3
myStr = 'google'

cCount = {}

for c in myStr:
    if c in cCount:
        cCount[c] += 1
    else:
        cCount[c] = 1
        
print(cCount)
    
# Final Exercise(Not my proudest implementation but I was honestly stressed by time)

## Import Python's Excel and XML Libraries
import openpyxl
import xml.etree.ElementTree as ET

## Function provided by VSeA team
def recursion(root, toBeReplaced, replaceBy):
    for x in range(0, len(root)):
        if (root[x].text == toBeReplaced):
            root[x].text = replaceBy
        else:
            recursion(root[x], toBeReplaced, replaceBy)

## Get lists of replacements(This can be better implemented)
def getReplacements(ws):
    replacements = []

    ### Should've just ignored the first row(Headers)
    for row in ws['A2':'X4']:
        replacements.append([[], []])

        i = 0
        for data in row:
            if (i % 2 == 0):
                replacements[-1][0].append(data.value)
            else:
                replacements[-1][1].append(data.value)
                
            i += 1

    return replacements

## Replace
def replace(inputFileName, outputFileName, replacements):
    tree = ET.parse(inputFileName)
        
    root = tree.getroot()

    ### This is dependent on the bad implementation of the previous function
    for i in range(0, len(replacements[0])):
        recursion(root, replacements[0][i], replacements[1][i])

    tree.write(outputFileName)

wb = openpyxl.load_workbook('Generationfile.xlsx')
ws1 = wb['Sheet1']

replacements = getReplacements(ws1)

for i in range(0, len(replacements)):
    replace('CanComm_RX_[ESP_HL_Radgeschw_02].xml', 'CanComm_RX_[ESP_HL_Radgeschw_02]_' + str(i) + '.xml', replacements[i])
