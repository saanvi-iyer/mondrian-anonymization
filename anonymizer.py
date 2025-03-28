"""
run basic_mondrian with given parameters
"""
import sys
import copy
import random
from mondrian import mondrian
from utils.read_adult_data import read_data as read_adult, read_tree as read_adult_tree
from utils.read_informs_data import read_data as read_informs, read_tree as read_informs_tree

DATA_SELECT = 'i'
DEFAULT_K = 20

def extend_result(val):
    return ','.join(val) if isinstance(val, list) else val

def write_to_file(result):
    with open("data/anonymized.data", "w") as output:
        for r in result:
            output.write(';'.join(map(extend_result, r)) + '\n')

def get_result_one(att_trees, data, k=DEFAULT_K):
    print("K={}".format(k))
    print("Mondrian")
    result, eval_result = mondrian(att_trees, data, k)
    write_to_file(result)
    print("NCP {:.2f}%\nRunning time {:.2f} seconds".format(eval_result[0], eval_result[1]))

def get_result_k(att_trees, data):
    data_back = copy.deepcopy(data)
    all_ncp, all_rtime = [], []
    for k in [2, 5, 10, 25, 50, 100]:
        print("#" * 30 + "\nK={}\nMondrian".format(k))
        _, eval_result = mondrian(att_trees, data, k)
        data = copy.deepcopy(data_back)
        all_ncp.append(round(eval_result[0], 2))
        all_rtime.append(round(eval_result[1], 2))
        print("NCP {:.2f}%\nRunning time {:.2f} seconds".format(eval_result[0], eval_result[1]))
    print("All NCP {}\nAll Running time {}".format(all_ncp, all_rtime))

def get_result_dataset(att_trees, data, k=DEFAULT_K, n=10):
    length = len(data)
    print("K={}".format(k))
    joint = 5000
    datasets = [joint * (i + 1) for i in range(length // joint)] + [length]
    all_ncp, all_rtime = [], []
    for pos in datasets:
        ncp, rtime = 0, 0
        print("#" * 30 + "\nSize of dataset {}".format(pos))
        for _ in range(n):
            temp = random.sample(data, pos)
            _, eval_result = mondrian(att_trees, temp, k)
            ncp += eval_result[0]
            rtime += eval_result[1]
        all_ncp.append(round(ncp / n, 2))
        all_rtime.append(round(rtime / n, 2))
        print("Average NCP {:.2f}%\nRunning time {:.2f} seconds".format(ncp / n, rtime / n))
    print("#" * 30 + "\nAll NCP {}\nAll Running time {}".format(all_ncp, all_rtime))

def get_result_qi(att_trees, data, k=DEFAULT_K):
    ls = len(data[0])
    all_ncp, all_rtime = [], []
    for i in range(1, ls):
        print("#" * 30 + "\nNumber of QI={}".format(i))
        _, eval_result = mondrian(att_trees, data, k, i)
        all_ncp.append(round(eval_result[0], 2))
        all_rtime.append(round(eval_result[1], 2))
        print("NCP {:.2f}%\nRunning time {:.2f} seconds".format(eval_result[0], eval_result[1]))
    print("All NCP {}\nAll Running time {}".format(all_ncp, all_rtime))

if __name__ == '__main__':
    FLAG = ''
    try:
        DATA_SELECT = sys.argv[1]
        FLAG = sys.argv[2]
    except IndexError:
        pass
    
    k = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_K
    
    if DATA_SELECT == 'i':
        RAW_DATA = read_informs()
        ATT_TREES = read_informs_tree()
    else:
        RAW_DATA = read_adult()
        ATT_TREES = read_adult_tree()
    
    print("#" * 30 + "\n{} data\n".format("Adult" if DATA_SELECT == 'a' else "INFORMS") + "#" * 30)
    
    if FLAG == 'k':
        get_result_k(ATT_TREES, RAW_DATA)
    elif FLAG == 'qi':
        get_result_qi(ATT_TREES, RAW_DATA)
    elif FLAG == 'data':
        get_result_dataset(ATT_TREES, RAW_DATA)
    elif FLAG in ('one', ''):
        get_result_one(ATT_TREES, RAW_DATA, k)
    else:
        print("Usage: python anonymizer.py [a | i] [k | qi | data | one]\n"
              "a: adult dataset, 'i': INFORMS dataset\n"
              "K: varying k, qi: varying qi numbers, data: varying dataset size, one: run once")
    
    print("Finish Basic_Mondrian!!")