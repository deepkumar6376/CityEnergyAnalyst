from multiprocessing import Pool
a=[]
def f(x):
    a.append(x*x)
    print a
    return a

if __name__ == '__main__':
    p = Pool(5)
    print(p.map(f, xrange(20)))