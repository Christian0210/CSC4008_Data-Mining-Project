import csv
import math


class Instance:
    def __init__(self, attr, iclass):
        self.attr = attr
        self.iclass = iclass


def read_file():
    attribute_name = []
    instances = []
    with open('credit-g.csv')as file:
        file_csv = csv.reader(file)
        for row in file_csv:
            if attribute_name == []:
                attribute_name = row[0: -1]
            else:
                attr = {}
                for i in range(0, len(row) - 1):
                    attr[attribute_name[i]] = row[i]
                ins = Instance(attr, row[-1])
                instances.append(ins)
    return instances


def normal(x, u, std):
    return math.exp(-(x - u) ** 2 / (2 * std ** 2)) / (math.sqrt(2 * math.pi) * std)


def main():
    attribute_name = ['checking_status', 'duration', 'credit_history', 'purpose', 'credit_amount', 'savings_status',
                      'employment', 'installment_commitment', 'personal_status', 'other_parties', 'residence_since',
                      'property_magnitude', 'age', 'other_payment_plans', 'housing', 'existing_credits',
                      'job', 'num_dependents', 'own_telephone', 'foreign_worker']
    attribute_discrete_name = ['checking_status', 'credit_history', 'purpose', 'savings_status', 'employment',
                               'installment_commitment', 'personal_status', 'other_parties', 'residence_since',
                               'property_magnitude', 'other_payment_plans', 'housing', 'job', 'own_telephone',
                               'foreign_worker']
    attribute_continuous_name = ['duration', 'credit_amount', 'age', 'existing_credits', 'num_dependents']

    attribute_type = {'checking_status': ['<0', '0<=X<200', '>=200', '\'no checking\''],
                      'credit_history': ['\'no credits/all paid\'', '\'all paid\'', '\'existing paid\'',
                                         '\'delayed previously\'', '\'critical/other existing credit\''],
                      'purpose': ['\'new car\'', '\'used car\'', 'furniture/equipment', 'radio/tv',
                                  '\'domestic appliance\'', 'repairs', 'education', 'vacation', 'retraining',
                                  'business', 'other'],
                      'savings_status': ['<100', '100<=X<500', '500<=X<1000', '>=1000', '\'no known savings\''],
                      'employment': ['unemployed', '<1', '1<=X<4', '4<=X<7', '>=7'],
                      'installment_commitment': ['1', '2', '3', '4'],
                      'personal_status': ['\'male div/sep\'', '\'female div/dep/mar\'', '\'male single\'',
                                          '\'male mar/wid\'', '\'female single\''],
                      'other_parties': ['none', '\'co applicant\'', 'guarantor'],
                      'residence_since': ['1', '2', '3', '4'],
                      'property_magnitude': ['\'real estate\'', '\'life insurance\'', 'car', '\'no known property\''],
                      'other_payment_plans': ['bank', 'stores', 'none'], 'housing': ['rent', 'own', '\'for free\''],
                      'job': ['\'unemp/unskilled non res\'', '\'unskilled resident\'', 'skilled',
                              '\'high qualif/self emp/mgmt\''], 'own_telephone': ['none', 'yes'],
                      'foreign_worker': ['yes', 'no']}

    class_type = ['good', 'bad']

    instances = read_file()

    n = len(instances)
    k = eval(input("Please input k for the k-fold cross-validation: "))
    step = int(n / k)
    base = instances + instances

    TP = 0
    FP = 0
    FN = 0
    TN = 0

    for i in range(k):

        test = base[i * step: min((i + 1) * step, n)]
        train = base[min((i + 1) * step, n): i * step + n]
        class1 = 0
        class2 = 0
        for instance in train:
            if instance.iclass == class_type[0]:
                class1 += 1
            else:
                class2 += 1
        p_class1 = class1 / len(train)
        p_class2 = class2 / len(train)

        sta1 = {}
        sta2 = {}
        for attribute in attribute_name:
            sta1[attribute] = {}
            sta2[attribute] = {}
            if attribute in attribute_discrete_name:
                for discrete_type in attribute_type[attribute]:
                    sta1[attribute][discrete_type] = 0
                    sta2[attribute][discrete_type] = 0
            else:
                sta1[attribute]['mean'] = 0
                sta2[attribute]['mean'] = 0
                sta1[attribute]['std'] = 0
                sta2[attribute]['std'] = 0

        for instance in train:
            for attribute in attribute_name:
                if attribute in attribute_discrete_name:
                    if instance.iclass == class_type[0]:
                        sta1[attribute][instance.attr[attribute]] += 1
                    else:
                        sta2[attribute][instance.attr[attribute]] += 1
                else:
                    if instance.iclass == class_type[0]:
                        sta1[attribute]['mean'] += eval(instance.attr[attribute])
                    else:
                        sta2[attribute]['mean'] += eval(instance.attr[attribute])

        for attribute in attribute_continuous_name:
            sta1[attribute]['mean'] /= class1
            sta2[attribute]['mean'] /= class2

        for instance in train:
            for attribute in attribute_continuous_name:
                if instance.iclass == class_type[0]:
                    sta1[attribute]['std'] += (sta1[attribute]['mean'] - eval(instance.attr[attribute])) ** 2
                else:
                    sta2[attribute]['std'] += (sta2[attribute]['mean'] - eval(instance.attr[attribute])) ** 2

        for attribute in attribute_continuous_name:
            sta1[attribute]['std'] = math.sqrt(sta1[attribute]['std'] / len(train))
            sta2[attribute]['std'] = math.sqrt(sta2[attribute]['std'] / len(train))

        tp = 0
        fp = 0
        fn = 0
        tn = 0
        for instance in test:
            p_X1 = 1
            p_X2 = 1
            for attribute in attribute_name:
                if attribute in attribute_discrete_name:
                    p_X1 *= (sta1[attribute][instance.attr[attribute]] + 1) / (class1 + len(attribute_type[attribute]))
                    p_X2 *= (sta2[attribute][instance.attr[attribute]] + 1) / (class2 + len(attribute_type[attribute]))
                else:
                    p_X1 *= normal(eval(instance.attr[attribute]), sta1[attribute]['mean'], sta1[attribute]['std'])
                    p_X2 *= normal(eval(instance.attr[attribute]), sta2[attribute]['mean'], sta2[attribute]['std'])
            p1 = p_X1 * p_class1
            p2 = p_X2 * p_class2
            if p1 > p2:
                if instance.iclass == class_type[0]:
                    tp += 1
                else:
                    fp += 1
            else:
                if instance.iclass == class_type[0]:
                    fn += 1
                else:
                    tn += 1

        TP += tp
        FP += fp
        FN += fn
        TN += tn

    print("Relation:".ljust(12), "german_credit")
    print("Instances:".ljust(12), n)
    print("Attributes:".ljust(12), len(attribute_name) + 1)
    for attribute in attribute_name:
        print("".ljust(12), attribute)
    print("".ljust(12), "class")
    print("Test mode:".ljust(12), f"{k}-fold cross_validation\n")

    print("=== Summary===\n")
    T = TP + TN
    F = n - TP - TN
    Tpercent = (TP + TN) / n * 100
    Fpercent = (n - TP - TN) / n * 100
    print("Correctly Classified Instances:".ljust(35), str(T).rjust(8), "%10.3f" % Tpercent, "%")
    print("Incorrectly Classified Instances:".ljust(35), str(F).rjust(8), "%10.3f" % Fpercent, "%")
    print("Total Number of Instances:".ljust(35), str(n).rjust(8))
    print()

    print("=== Detail Accuracy By Class ===\n")
    print("Precision".ljust(11), "Recall".ljust(11), "Specificity".ljust(11), "F-Measure".ljust(11), "Class")
    if TP + FP == 0:
        precision = 0
    else:
        precision = TP / (TP + FP)
    if TP + FN == 0:
        recall = 0
    else:
        recall = TP / (TP + FN)
    if TN + FP == 0:
        specificity = 0
    else:
        specificity = TN / (TN + FP)
    f = 2 * precision * recall / (precision + recall)
    print("%-11.3f" % precision, "%-11.3f" % recall, "%-11.3f" % specificity, "%-11.3f" % f, class_type[0])
    print()

    print("=== Confusion Matrix ===\n")
    print("a".rjust(4), "b".rjust(4), "   <-- classifed as")
    print(str(TP).rjust(4), str(FN).rjust(4), f" |   a = {class_type[0]}")
    print(str(FP).rjust(4), str(TN).rjust(4), f" |   b = {class_type[1]}")


if __name__ == "__main__":
    main()
