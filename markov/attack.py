from train import *
from guess import *
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Markov-based Password Cracking")
    parser.add_argument('--path', type=str, default='data/rockyou.txt', help='the path of password file')
    parser.add_argument('--number', type=float, default=2000000, help='the total of train and test simpled from password file')
    parser.add_argument('--seed', type=int, default=2, help='random seed')
    parser.add_argument('--order', type=int, default=3, help='')
    opt = parser.parse_args()

    start_symbol = '#' * opt.order
    path = 'order{}/order{}_{}_{}.pickle'.format(opt.order, opt.order, opt.seed, opt.number)
    if not os.path.exists(path):
        print("Loading Password File ...")
        preprocess(opt.path, opt.seed, opt.number)
        print("Finished ...")
        passwd = loadpass('data/trainword.txt',start_symbol)
        base = statistic(passwd, opt.order)
        laplace(base, opt.order, opt.seed, opt.number)

    print("Guessing Password ...")
    testpd = testpass('data/testword.txt')
    with open(path.format(opt.order, opt.order), 'rb') as file:
        base = pickle.load(file)
    guesser = Guess(base, start_symbol, opt.order, testpd)

    n = opt.number / 2
    m = 100000
    thre = threhold(m,n)
    guesser.initqueue(thre[0])

    with open('order{}/memory.txt'.format(opt.order),'w+') as f:
        num = 0
        k = 0
        while guesser.flag:

            k = int(guesser.true_guess / m)
            guesser.insertqueue(thre[k])
            num += 1
            if num % 1000 == 0:
                f.write(str(guesser.true_guess) + ' / ' + str(guesser.num_guess) + '\n')
                print("GUESS: {} / {}".format(guesser.true_guess, guesser.num_guess))

if __name__ == "__main__":

    main()
