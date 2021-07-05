import re
import sys
import copy
from queue import PriorityQueue
import itertools

Lp = re.compile('L')
Dp = re.compile('D')
Sp = re.compile('S')

# 导入测试集
def load_testword(path):
    
    testword = {}
    with open(path, encoding='utf-8', errors='ignore') as wordList:
        for line in wordList:
            word = line.strip()
            if word in testword:
                testword[word] += 1
            else:
                testword.setdefault(word, 1)
    return testword

def parsebase(base):
    # 'L6D1' --> ['L6','D1']
    pa = re.compile(r'[LDS]\d+', re.ASCII)
    baseList = re.findall(pa, base)
    return baseList

def findalphas(base):
    
    alphas = []
    for i, s in enumerate(base):
        if Lp.match(s):
            index = extractindex(base, i)
            alphas.append(index)
    return alphas

def extractindex(base, pv):
    # index[0]: pv点之前字段总长度
    # index[1]: 当前pv点字段长度
    index = [0] * 2
    prev = "".join(base[0: pv])
    index[0] = sum(map(int, re.findall(r'\d+', prev)))
    index[1] = re.search(r'\d+', base[pv]).group()

    return index

class Guess:
    
    def __init__(self, model, testword, pwalpha):
        
        self.model = model
        self.num_guess = 0     # 总共猜测的次数
        self.true_guess = 0    # 猜测正确的次数
        self.queue = PriorityQueue()
        self.testword = testword
        self.pwalpha = pwalpha
        self.flag = 1

    # 初始化队列
    def initqueue(self):
        
        for base in self.model.bases:
            
            qobject = [None] * 6
            qobject[1] = parsebase(base)    # 'L6D1' --> ['L6','D1']
            qobject[5] = parsebase(base)    # 'L6D1' --> ['L6','D1']
            qobject[2] = 0    #
            prob = self.model.bases[base]
            
            preterminal = ""
            
            for i, s in enumerate(qobject[1]):
                
                if Lp.match(s):
                    preterminal += s
                    continue
                else:
                    if Dp.match(s):
                        preterminal += self.model.digits[s][0][0]
                        qobject[5][i] = self.model.digits[s][0][0]
                        prob *= self.model.digits[s][0][1]    # 口令概率值
                    elif Sp.match(s):
                        preterminal += self.model.symbols[s][0][0]
                        qobject[5][i] = self.model.symbols[s][0][0]
                        prob *= self.model.symbols[s][0][1]    # 口令概率值
                    else:
                        print("error")
                        sys.exit(1)
            if prob < 0.000001:    # 如果该口令模式的概率值小于0.000001,则不进入队列
                continue
            qobject[3] = preterminal
            qobject[4] = [0] * len(qobject[1])
            qobject[0] = prob
            self.queue.put(qobject)

    # 插入队列
    def queueinsert(self):
        
        if self.queue.empty():    # 判断队列是否为空
            print("all possible gussess have be output")
            print("GUESS:", self.true_guess)
            print("TRUE:", self.num_guess)
            self.flag = 0
            return
           
        qobject = self.queue.get()
        pv = qobject[2]    # 指示下一个替换的位置
        base = qobject[1]
        alphaindex = findalphas(base)
        
        for i, s in enumerate(base):
            if i < pv or Lp.match(s):
                continue
            index = extractindex(base, i)
            if Dp.match(s) and qobject[4][i] == self.model.digitstats[s]:     # 判断同类型字段是否遍历完
                continue
            if Sp.match(s) and qobject[4][i] == self.model.symbolstats[s]:     # 判断同类型字段是否遍历完
                continue
            newobject = copy.deepcopy(qobject)
            newobject[2] = i     # 设置pv值
            newobject[4][i] += 1   # 指示该字段列表中下一个替换的位置
            if Dp.match(s):
                original = self.model.digits[s][qobject[4][i]]
                new = self.model.digits[s][newobject[4][i]]
                newobject[5][i] = new[0]
            else:
                original = self.model.symbols[s][qobject[4][i]]
                new = self.model.symbols[s][newobject[4][i]]
                newobject[5][i] = new[0]
            newobject[0] = qobject[0] / original[1] * new[1]
            newobject[3] = ''.join(newobject[5])
            if newobject[0] < 0.000001:    # 如果该口令模式的概率值小于0.000001,则不进入队列
                continue
            self.queue.put(newobject)
            
        return (alphaindex, qobject[3], qobject[0])

    # 生成猜解口令
    def guesspw(self, preterminal):
        
        alphaindex = preterminal[0]
        pw = preterminal[1]
        pro = preterminal[2]
        num = 0

        if not alphaindex:
            print(pw)
        else:
            replacements = []
            for index in alphaindex:    # 一个口令结构模式中可能含有多个'L'字段
                s = 'L' + index[1]
                replacements.append(self.model.alphas[s])
            
            # [['a', 'b'], ['ab', 'cd']] --> [('a','ab'),('a', 'cd'),('b','ab'),('b','cd')]
            replacements = list(itertools.product(*replacements))
            filepath = './guess/' + list(self.model.bases.keys())[0] + '.txt'
            with open(filepath, 'a+') as f:
                for rep in replacements:
                    pwd = pw
                    pwdpro = pro
                    for i, word in enumerate(rep):
                        start = alphaindex[i][0]
                        s = 'L' + alphaindex[i][1]
                        pwd = pwd.replace(s, word, 1)
                        pwdpro *= self.pwalpha[s][word]
                    if pwdpro < 0.000000001:    # 如果该口令的概率值小于0.000000001,则不进行猜解
                        # print('..................................................' + str(self.num_guess))
                        continue
                    print(pwd)
                    num += 1
                    f.write(pwd + '\t' + str(pwdpro) + '\n')
                    if pwd in self.testword:
                        self.true_guess += self.testword[pwd]
                        del self.testword[pwd]
        self.num_guess += num
