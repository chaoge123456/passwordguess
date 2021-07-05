from train import *
from guess import *
import argparse
from collections import OrderedDict

def main():
    parser = argparse.ArgumentParser(description="PCFG: Password Cracking Using Probabilistic Context-Free Grammars")
    parser.add_argument('--path', type=str, default='myspace.txt', help='the path of password file')
    parser.add_argument('--eps', type=float, default=0.4, help='split the train and test')
    parser.add_argument('--seed', type=int, default=0, help='random seed')
    opt = parser.parse_args()

    # preprocess(opt.path, opt.seed, opt.eps)    #原始数据预处理预处理

    trainword = loadpass('trainword.txt')    # 导入训练集
    oribase, orialpha, oridigit, orispecial = statistic(trainword)

    alphatodict(orialpha)   # 字典由训练集中提取的英文字母字段生成，生成wordlist.txt

    base_probability(oribase)   # 每种口令结构出现的频率
    oribase = sorted(oribase.items(), key=lambda t: t[1], reverse=True)    # 排序
    testword = load_testword('testword.txt')    # 导入测试集
    true_guess = 0    # 统计猜解次数
    num_guess = 0    # 统计猜解正确的次数

    for i in oribase:    # 每次使用一种类型的口令结构去猜解
        base = OrderedDict([i])
        alpha = copy.deepcopy(orialpha)
        digit = copy.deepcopy(oridigit)
        special = copy.deepcopy(orispecial)

        model = Train(base, digit, special)
        model.order()
        model.loadict('wordlist.txt')
        probability(alpha)

        # 开始猜测口令
        guesser = Guess(model, testword, alpha)
        guesser.initqueue()   # 初始化队列
        while True:
            preterminal = guesser.queueinsert()
            if guesser.flag:    # 判断队列是否为空
                guesser.guesspw(preterminal)
            else:
                break
        true_guess += guesser.true_guess
        num_guess += guesser.num_guess
        testword = guesser.testword
        with open('memory.txt', 'a+') as memory:
            memory.write(str(true_guess) + ' / ' + str(num_guess) + '\n')

if __name__ == "__main__":
    main()
