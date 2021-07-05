import re
import random
import pickle

# 读取数据集预处理
def preprocess(path, seed, number = 2000000):

    passwd = []
    exp = re.compile(r'[^\x20-\x7e]')

    with open(path, encoding="ISO-8859-1") as wordlist:
        for i,line in enumerate(wordlist):
            try:
                wl = line.strip().split(' ', 1)
                num = int(wl[-2])
                pd = wl[-1]
                if exp.search(pd) or ' ' in pd or len(pd) >= 21: # 过滤非ASCLL字符和空格
                    continue
                else:
                    passwd.extend([pd]*num)
            except Exception:
                #print("Exception: ",line)
                continue

    # 切分数据集（训练集和测试集）
    random.seed(seed)
    r = random.sample(range(0, len(passwd)), number)
    lt = [passwd[i] for i in r]
    testword = lt[0:int(number / 2)]
    trainword = lt[int(number / 2):]
    
    with open("data/trainword.txt", "w") as f:
        for pd in trainword:
            f.write(pd + '\n')
        
    with open("data/testword.txt", "w") as f:
        for pd in testword:
            f.write(pd + '\n')

# 读取训练集
def loadpass(path, start_symbol):

    passwd = {}
    with open(path, 'r') as wordList:
        for line in wordList:
            line = start_symbol + line
            if line in passwd:
                passwd[line] += 1
            else:
                passwd.setdefault(line, 1)
    return passwd

# 统计频数
def statistic(passwd, order):

    base = {}
    for key, value in passwd.items():

        l = len(key)
        for ord in range(order, order+1):
            for i in range(l-ord):
                ps = key[i:i+ord]
                qs = key[i+ord]

                if ps in base:
                    if qs in base[ps]:
                        base[ps][qs] += value
                    else:
                        base[ps].setdefault(qs, value)
                else:
                    base.setdefault(ps, {})
                    base[ps].setdefault(qs, value)
    return base

# laplace平滑和排序
def laplace(base, order, seed, number):

    for key, value in base.items():
        num = sum(value.values())
        for k, v in value.items():
            base[key][k] = (v * 1.0 + 0.01) / (num + 0.96)

    for key, value in base.items():
        base[key] = sorted(value.items(), key=lambda t: t[1], reverse=True)

    with open('./order{}/order{}_{}_{}.pickle'.format(order, order, seed, number), 'wb') as file:
        pickle.dump(base, file)

