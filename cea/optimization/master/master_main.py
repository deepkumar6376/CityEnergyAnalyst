"""
===========================
Evolutionary algorithm main
===========================

"""
from __future__ import division
import time
import json
import os
import cea.optimization.master.crossover as cx
import cea.optimization.master.evaluation as evaluation
from deap import base
from deap import creator
from deap import tools
import multiprocessing as mp
import cea.optimization.master.generation as generation
import mutations as mut
import selection as sel

__author__ =  "Sreepathi Bhargava Krishna"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = [ "Sreepathi Bhargava Krishna", "Thuy-An Nguyen", "Tim Vollrath", "Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"

def f(x):
    return x*x

if __name__ == '__main__':
    pool = mp.Pool(processes=4)

    print pool.map(f, range(100))

    res = pool.apply_async(f, (20,))
    print res.get(timeout=1)

    for i in range(4):
        res = pool.apply_async(f,(i,))
        print (res.get(timeout=1))

    multiple_results = [pool.apply_async(f, (i, )) for i in range(4)]
    print (res.get(timeout=1) for res in multiple_results)


