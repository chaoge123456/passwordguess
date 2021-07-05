import re
import random
import sys

# 读取数据集预处理
def preprocess(path, seed, eps):

    passwd = []
    exp = re.compile(r'[^\x00-\x7f]')
    try:
        with open(path, encoding='utf-8') as wordlist:
            for line in wordlist:
                wl = line.strip().split(' ', 1)
                num = int(wl[-2])
                pd = wl[-1]
                if exp.search(pd) or ' ' in pd: # 过滤非ASCLL字符和空格
                    continue
                else:
                    passwd.extend([pd]*num)
    except FileNotFoundError:
        print("The password file does not exist", file=sys.stderr)

    # 切分数据集（训练集和测试集）
    random.seed(seed)
    l = random.sample(range(0,len(passwd)), int(len(passwd)*eps))
    testword = [passwd[i] for i in l]
    trainword = [passwd[i] for i in range(0, len(passwd)) if i not in l]
    
    with open("trainword.txt", "w") as f:
        for pd in trainword:
            f.write(pd + '\n')
        
    with open("testword.txt", "w") as f:
        for pd in testword:
            f.write(pd + '\n')

# 读取数据集
def loadpass(path):

    passwd = []
    with open(path, encoding='utf-8', errors='ignore') as wordList:
        for line in wordList:
            passwd.append(line.strip())
    return passwd

# 统计每种结构以及字段出现的次数
def count(part, m, a):

    if m in a:
        if part in a[m]:
            a[m][part] += 1
        else:
            a[m].setdefault(part, 1)
    else:
        a.setdefault(m, {})
        a[m].setdefault(part, 1)

# 将次数转化为频率
def probability(d):

    for key in d.keys():
        num = sum(d[key].values())
        for k in d[key].keys():
            d[key][k] = d[key][k]*1.0 / num

# 将次数转化为频率
def base_probability(d):

    num = sum(d.values())
    for key in d.keys():
        d[key] = d[key] * 1.0 / num

# 口令切割统计
def statistic(trainword):

    mode = {}
    alpha = {}
    digit = {}
    special = {}

    pattern = re.compile(r'[A-Za-z]*|[0-9]*|[^a-zA-Z0-9]*', re.ASCII)
    for pd in trainword:
        s = ''
        parts = re.findall(pattern, pd)
        for part in parts:
            if part == '':
                continue
            else:
                l = len(part)
                if part.isdigit():
                    m = 'D'+str(l)
                    count(part, m, digit)
                elif part.isalpha():
                    m = 'L'+str(l)
                    count(part, m, alpha)
                else:
                    m = 'S'+str(l)
                    count(part, m, special)
            s += m
        if s in mode:
            mode[s] += 1
        else:
            mode.setdefault(s, 1)
    return mode, alpha, digit, special

# 由训练集中提取的字母段生成字典
def alphatodict(alpha):

    d = {}
    with open('wordlist.txt', 'w') as f:
        for key, value in alpha.items():
            for k in list(value.keys()):
                f.write(k+'\n')


class Train:
    
    def __init__(self, bases, digits, symbols):
        
        self.bases = bases # 口令结构
        self.digits = digits # 数值字段
        self.symbols = symbols # 特殊符号字段
        self.alphas = {} # 字典
        self.digitstats = {} # 训练集中每种类型数值字段出现的次数
        self.symbolstats = {} # 训练集中每种类型特殊符号字段出现的次数
        self.dictstats = {} # 字典中不同长度类型出现的次数
        self.dsize = 0 # 字典大小
    
    def order(self):
        
        probability(self.digits) # 计算数值字段出现的频率
        probability(self.symbols)  # 计算特殊符号字段出现的频率

        # 数值字段排序
        for key, value in self.digits.items():
            self.digits[key] = sorted(value.items(),key=lambda t:t[1], reverse=True)
            self.digitstats[key] = len(self.digits[key])-1

        # 特殊符号字段排序
        for key, value in self.symbols.items():
            self.symbols[key] = sorted(value.items(),key=lambda t:t[1], reverse=True)
            self.symbolstats[key] = len(self.symbols[key])-1
    # 导入字典
    def loadict(self, path):

        with open(path, encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                self.dsize += 1
                l = len(line)
                s = 'L' + str(l)
                if s not in self.alphas:
                    self.alphas[s] = []
                self.alphas[s].append(line)
        for la in self.alphas:
            self.dictstats[la] = len(self.alphas[la])