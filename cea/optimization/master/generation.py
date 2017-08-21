"""
==================
Create individuals
==================

"""
from __future__ import division
import random
from numpy.random import random_sample
from itertools import izip

__author__ =  "Thuy-An Nguyen"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = [ "Thuy-An Nguyen", "Tim Vollrath", "Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"

def generate_main(lower_bound, upper_bound):
    """
    Creates an individual configuration for the evolutionary algorithm based on the lower and upper bounds

    :param nBuildings: number of buildings
    :param gv: global variables class
    :type nBuildings: int
    :type gv: class
    :return: individual: representation of values taken by the individual
    :rtype: list
    """

    # randomly generate individual betweeen the lower and upper bounds

    individual = []
    size = len(lower_bound)

    for i in range(size):
        individual[i] = (upper_bound[i] - lower_bound[i]) * random.random() + lower_bound[i]

    return individual


    
    # Allocation of Shares
    def cuts(ind, nPlants, irank):
        cuts = sorted(random_sample(nPlants - 1) * 0.99 + 0.009)    
        edge = [0] + cuts + [1]
        share = [(b - a) for a, b in izip(edge, edge[1:])]
        
        n = len(share)
        sharetoallocate = 0
        rank = irank
        while sharetoallocate < n:
            if ind[rank] > 0:
                ind[rank+1] = share[sharetoallocate]
                sharetoallocate += 1
            rank += 2
    
    cuts(individual, countDHN, 0)

    if countSolar > 0:
        cuts(individual, countSolar, gv.nHeat * 2 + gv.nHR)

    # Connection of the buildings
    for building in range(nBuildings):
        choice_buildCon = random.randint(0,1)
        individual[index] = choice_buildCon
        index += 1

    
    return individual






