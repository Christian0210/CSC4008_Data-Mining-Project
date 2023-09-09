import xlrd


class treeNode():
    def __init__(self, nodeName, parentNode, count):
        self.nodeName = nodeName
        self.parentNode = parentNode
        self.childNodes = {}
        self.nextLink = None
        self.count = count

    def increte(self, count):
        self.count += count

    def display(self, level=1):
        print(level * "-", self.nodeName, self.count)
        for child in self.childNodes.values():
            child.display(level + 1)


def updateHeader(updateNode, targetNode):
    while updateNode.nextLink != None:
        updateNode = updateNode.nextLink
    updateNode.nextLink = targetNode


def updateTree(orderItems, rootTree, headerTable, count):
    if orderItems[0] in rootTree.childNodes:
        rootTree.childNodes[orderItems[0]].increte(count)
    else:
        rootTree.childNodes[orderItems[0]] = treeNode(orderItems[0], rootTree, count)
        if headerTable[orderItems[0]][1] == None:
            headerTable[orderItems[0]][1] = rootTree.childNodes[orderItems[0]]
        else:
            updateHeader(headerTable[orderItems[0]][1], rootTree.childNodes[orderItems[0]])
    if len(orderItems) > 1:
        updateTree(orderItems[1::], rootTree.childNodes[orderItems[0]], headerTable, count)


def craeteHeaderTable(dataSet, minSup=1):
    headerTable = {}
    for transaction in dataSet:
        for item in transaction:
            headerTable[item] = headerTable.get(item, 0) + dataSet[transaction]
    for key in list(headerTable.keys()):
        if headerTable[key] < minSup:
            del (headerTable[key])
    return headerTable


def createTree(dataSet, minSup=1):
    headerTable = craeteHeaderTable(dataSet, minSup)
    if len(headerTable) == 0:
        return None, None
    for key in headerTable:
        headerTable[key] = [headerTable[key], None]
    rootTree = treeNode("Null Set", None, 1)
    for transaction, count in dataSet.items():
        localID = {}
        for transact in transaction:
            if transact in headerTable.keys():
                localID[transact] = headerTable[transact][0]
        if len(localID) > 0:
            oderItems = [v[0] for v in sorted(localID.items(), key=lambda p: p[1], reverse=True)]
            updateTree(oderItems, rootTree, headerTable, count)
    return rootTree, headerTable


def loadSimpleData():
    data = xlrd.open_workbook('AS5 supermarket_attribute_name.xlsx')
    table = data.sheet_by_name('Sheet 1 - Supermarket_attribute')

    n = table.nrows
    attribute = table.col_values(1)
    attrindex = []

    for i in range(0, n - 1):
        if attribute[i].find('department') < 0:
            attrindex.append(i)

    data = xlrd.open_workbook('AS5 supermarket.xlsx')
    table = data.sheet_by_name('supermarket')

    m = table.nrows
    itemset = []

    for i in range(1, m):
        c = []
        for j in range(0, n):
            if j in attrindex:
                yn = table.cell(i, j).value
                if yn != '?':
                    c.append(attribute[j])
        itemset.append(c)
    return itemset


def createInitset(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict


def findPrefixPath(baseRequenceList, treeNode):
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nextLink
    return condPats


def ascendTree(leafNode, prefixPath):
    if leafNode.parentNode != None:
        prefixPath.append(leafNode.nodeName)
        ascendTree(leafNode.parentNode, prefixPath)


def mineTree(rootTree, headerTable, minSup, preFix, f2Itemset, f3Itemset, f4Itemset):
    bigL = {v[0]:v[1][0] for v in sorted(headerTable.items(), key=lambda p: str(p[1][0]))}
    for basePat, freq in bigL.items():
        newFreqSet = preFix.copy()
        newFreqSet.add(basePat)
        if (len(newFreqSet) == 2):
            f2Itemset.append([newFreqSet, freq])
        if (len(newFreqSet) == 3):
            f3Itemset.append([newFreqSet, freq])
        if (len(newFreqSet) == 4):
            f4Itemset.append([newFreqSet, freq])
        conditionPatternBases = findPrefixPath(basePat, headerTable[basePat][1])
        myCondTree, myHead = createTree(conditionPatternBases, minSup)
        if myHead != None:
            mineTree(myCondTree, myHead, minSup, newFreqSet, f2Itemset, f3Itemset, f4Itemset)


def takesupport(elem):
    return elem[1]


dataSet = loadSimpleData()
n = len(dataSet)
transactionDict = createInitset(dataSet)
rootTree, headerTable = createTree(transactionDict)
f2Itemset = []
f3Itemset = []
f4Itemset = []
mineTree(rootTree, headerTable, 500, set([]), f2Itemset, f3Itemset, f4Itemset)

print("frequent 2-itemset")
f2Itemset.sort(key=takesupport, reverse=True)
for i in range(10):
    print(str(f2Itemset[i][0]).ljust(75), f2Itemset[i][1]/n)
print("\n")

print("frequent 3-itemset")
f3Itemset.sort(key=takesupport, reverse=True)
for i in range(10):
    print(str(f3Itemset[i][0]).ljust(75), f3Itemset[i][1]/n)
print("\n")

print("frequent 4-itemset")
f4Itemset.sort(key=takesupport, reverse=True)
for i in range(10):
    print(str(f4Itemset[i][0]).ljust(75), f4Itemset[i][1]/n)
