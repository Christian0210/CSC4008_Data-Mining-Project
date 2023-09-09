import xlrd


def load_data_set():
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


def create_C1(data_set):
    C1 = set()
    for t in data_set:
        for item in t:
            item_set = frozenset([item])
            C1.add(item_set)
    return C1


def is_apriori(Ck_item, Lksub1):
    for item in Ck_item:
        sub_Ck = Ck_item - frozenset([item])
        if sub_Ck not in Lksub1:
            return False
    return True


def create_Ck(Lksub1, k):
    Ck = set()
    len_Lksub1 = len(Lksub1)
    list_Lksub1 = list(Lksub1)
    for i in range(len_Lksub1):
        for j in range(1, len_Lksub1):
            l1 = list(list_Lksub1[i])
            l2 = list(list_Lksub1[j])
            l1.sort()
            l2.sort()
            if l1[0:k - 2] == l2[0:k - 2]:
                Ck_item = list_Lksub1[i] | list_Lksub1[j]
                # pruning
                if is_apriori(Ck_item, Lksub1):
                    Ck.add(Ck_item)
    return Ck


def generate_Lk_by_Ck(data_set, Ck, min_support, support_data):
    Lk = set()
    item_count = {}
    for t in data_set:
        for item in Ck:
            if item.issubset(t):
                if item not in item_count:
                    item_count[item] = 1
                else:
                    item_count[item] += 1
    t_num = float(len(data_set))
    for item in item_count:
        if (item_count[item] / t_num) >= min_support:
            Lk.add(item)
            support_data[item] = item_count[item] / t_num
    return Lk


def generate_L(data_set, k, min_support):
    support_data = {}
    C1 = create_C1(data_set)
    L1 = generate_Lk_by_Ck(data_set, C1, min_support, support_data)
    Lksub1 = L1.copy()
    L = []
    L.append(Lksub1)
    for i in range(2, k + 1):
        Ci = create_Ck(Lksub1, i)
        Li = generate_Lk_by_Ck(data_set, Ci, min_support, support_data)
        Lksub1 = Li.copy()
        L.append(Lksub1)
    return L, support_data


def takesupport(elem):
    return elem[1]


data_set = load_data_set()
L, support_data = generate_L(data_set, k=4, min_support=0.2)
output = []
for Lk in L:
    print("=" * 100)
    print("frequent " + str(len(list(Lk)[0])) + "-itemsets" + " "*60 + "support")
    print("=" * 100)
    output = []
    for freq_set in Lk:
        output_set = []
        for item in freq_set:
            output_set.append(item)
        output.append((output_set, support_data[freq_set]))
    output.sort(key=takesupport, reverse=True)
    for i in range(0, 10):
        print(str(output[i][0]).ljust(75), output[i][1])
    print('\n')
