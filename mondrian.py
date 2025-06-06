#!/usr/bin/env python
# coding=utf-8

import pdb
import random
from models.numrange import NumRange
from models.gentree import GenTree
from utils.utility import cmp_str
import time

__DEBUG = False
QI_LEN = 10
GL_K = 0
RESULT = []
ATT_TREES = []
QI_RANGE = []
IS_CAT = []

class Partition(object):
    def __init__(self, data, width, middle):
        self.member = list(data)
        self.width = list(width)
        self.middle = list(middle)
        self.allow = [1] * QI_LEN

    def __len__(self):
        return len(self.member)

def get_normalized_width(partition, index):
    if IS_CAT[index] is False:
        low = partition.width[index][0]
        high = partition.width[index][1]
        width = float(ATT_TREES[index].sort_value[high]) - float(ATT_TREES[index].sort_value[low])
    else:
        width = partition.width[index]
    return width * 1.0 / QI_RANGE[index]

def choose_dimension(partition):
    max_width = -1
    max_dim = -1
    for i in range(QI_LEN):
        if partition.allow[i] == 0:
            continue
        normWidth = get_normalized_width(partition, i)
        if normWidth > max_width:
            max_width = normWidth
            max_dim = i
    if max_width > 1:
        print("Error: max_width > 1")
        pdb.set_trace()
    if max_dim == -1:
        print("cannot find the max dim")
        pdb.set_trace()
    return max_dim

def frequency_set(partition, dim):
    frequency = {}
    for record in partition.member:
        try:
            frequency[record[dim]] += 1
        except KeyError:
            frequency[record[dim]] = 1
    return frequency

def find_median(partition, dim):
    frequency = frequency_set(partition, dim)
    splitVal = ''
    value_list = frequency.keys()
    value_list.sort(cmp=cmp_str)
    total = sum(frequency.values())
    middle = total / 2
    if middle < GL_K or len(value_list) <= 1:
        return ('', '', value_list[0], value_list[-1])
    index = 0
    split_index = 0
    for i, t in enumerate(value_list):
        index += frequency[t]
        if index >= middle:
            splitVal = t
            split_index = i
            break
    else:
        print("Error: cannot find splitVal")
    try:
        nextVal = value_list[split_index + 1]
    except IndexError:
        nextVal = splitVal
    return (splitVal, nextVal, value_list[0], value_list[-1])

def split_numerical_value(numeric_value, splitVal):
    split_num = numeric_value.split(',')
    if len(split_num) <= 1:
        return split_num[0], split_num[0]
    else:
        low = split_num[0]
        high = split_num[1]
        if low == splitVal:
            lvalue = low
        else:
            lvalue = low + ',' + splitVal
        if high == splitVal:
            rvalue = high
        else:
            rvalue = splitVal + ',' + high
        return lvalue, rvalue

def split_numerical(partition, dim, pwidth, pmiddle):
    sub_partitions = []
    (splitVal, nextVal, low, high) = find_median(partition, dim)
    p_low = ATT_TREES[dim].dict[low]
    p_high = ATT_TREES[dim].dict[high]
    if low == high:
        pmiddle[dim] = low
    else:
        pmiddle[dim] = low + ',' + high
    pwidth[dim] = (p_low, p_high)
    if splitVal == '' or splitVal == nextVal:
        return []
    middle_pos = ATT_TREES[dim].dict[splitVal]
    lmiddle = pmiddle[:]
    rmiddle = pmiddle[:]
    lmiddle[dim], rmiddle[dim] = split_numerical_value(pmiddle[dim], splitVal)
    lhs = []
    rhs = []
    for temp in partition.member:
        pos = ATT_TREES[dim].dict[temp[dim]]
        if pos <= middle_pos:
            lhs.append(temp)
        else:
            rhs.append(temp)
    lwidth = pwidth[:]
    rwidth = pwidth[:]
    lwidth[dim] = (pwidth[dim][0], middle_pos)
    rwidth[dim] = (ATT_TREES[dim].dict[nextVal], pwidth[dim][1])
    sub_partitions.append(Partition(lhs, lwidth, lmiddle))
    sub_partitions.append(Partition(rhs, rwidth, rmiddle))
    return sub_partitions

def split_categorical(partition, dim, pwidth, pmiddle):
    sub_partitions = []
    splitVal = ATT_TREES[dim][partition.middle[dim]]
    sub_node = [t for t in splitVal.child]
    sub_groups = []
    for i in range(len(sub_node)):
        sub_groups.append([])
    if len(sub_groups) == 0:
        return []
    for temp in partition.member:
        qid_value = temp[dim]
        for i, node in enumerate(sub_node):
            try:
                node.cover[qid_value]
                sub_groups[i].append(temp)
                break
            except KeyError:
                continue
        else:
            print("Generalization hierarchy error!")
    flag = True
    for index, sub_group in enumerate(sub_groups):
        if len(sub_group) == 0:
            continue
        if len(sub_group) < GL_K:
            flag = False
            break
    if flag:
        for i, sub_group in enumerate(sub_groups):
            if len(sub_group) == 0:
                continue
            wtemp = pwidth[:]
            mtemp = pmiddle[:]
            wtemp[dim] = len(sub_node[i])
            mtemp[dim] = sub_node[i].value
            sub_partitions.append(Partition(sub_group, wtemp, mtemp))
    return sub_partitions

def split_partition(partition, dim):
    pwidth = partition.width
    pmiddle = partition.middle
    if IS_CAT[dim] is False:
        return split_numerical(partition, dim, pwidth, pmiddle)
    else:
        return split_categorical(partition, dim, pwidth, pmiddle)

def adjust_k(partition, current_k):
    min_size = min([len(p.member) for p in RESULT] + [len(partition.member)]) if RESULT else len(partition.member)
    return max(current_k, int(min_size / 2)) if min_size < current_k * 2 else current_k

def anonymize(partition, k):
    global GL_K
    GL_K = k
    if check_splitable(partition) is False:
        RESULT.append(partition)
        return
    dim = choose_dimension(partition)
    if dim == -1:
        print("Error: dim=-1")
        pdb.set_trace()
    sub_partitions = split_partition(partition, dim)
    if len(sub_partitions) == 0:
        partition.allow[dim] = 0
        anonymize(partition, k)
    else:
        new_k = adjust_k(partition, k)
        GL_K = new_k
        for sub_p in sub_partitions:
            anonymize(sub_p, new_k)

def check_splitable(partition):
    temp = sum(partition.allow)
    if temp == 0:
        return False
    return True

def init(att_trees, data, k, QI_num=-1):
    global GL_K, RESULT, QI_LEN, ATT_TREES, QI_RANGE, IS_CAT
    ATT_TREES = att_trees
    for t in att_trees:
        if isinstance(t, NumRange):
            IS_CAT.append(False)
        else:
            IS_CAT.append(True)
    if QI_num <= 0:
        QI_LEN = len(data[0]) - 1
    else:
        QI_LEN = QI_num
    GL_K = k
    RESULT = []
    QI_RANGE = []

def mondrian(att_trees, data, k, QI_num=-1):
    init(att_trees, data, k, QI_num)
    result = []
    middle = []
    wtemp = []
    for i in range(QI_LEN):
        if IS_CAT[i] is False:
            QI_RANGE.append(ATT_TREES[i].range)
            wtemp.append((0, len(ATT_TREES[i].sort_value) - 1))
            middle.append(ATT_TREES[i].value)
        else:
            QI_RANGE.append(len(ATT_TREES[i]['*']))
            wtemp.append(len(ATT_TREES[i]['*']))
            middle.append('*')
    whole_partition = Partition(data, wtemp, middle)
    start_time = time.time()
    anonymize(whole_partition, k)
    rtime = float(time.time() - start_time)
    ncp = 0.0
    for partition in RESULT:
        r_ncp = 0.0
        for i in range(QI_LEN):
            r_ncp += get_normalized_width(partition, i)
        temp = partition.middle
        for i in range(len(partition)):
            result.append(temp + [partition.member[i][-1]])
        r_ncp *= len(partition)
        ncp += r_ncp
    ncp /= QI_LEN
    ncp /= len(data)
    ncp *= 100
    if len(result) != len(data):
        print("Losing records during anonymization!!")
        pdb.set_trace()
    if __DEBUG:
        print("K=%d" % k)
        print("size of partitions")
        print(len(RESULT))
        temp = [len(t) for t in RESULT]
        print(sorted(temp))
        print("NCP = %.2f %%" % ncp)
    return (result, (ncp, rtime))