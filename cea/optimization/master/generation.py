"""
==================
Create individuals
==================

"""
from __future__ import division
import random
from numpy.random import random_sample
from itertools import izip
import cea.optimization.optimization_settings


__author__ =  "Thuy-An Nguyen"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = [ "Thuy-An Nguyen", "Tim Vollrath", "Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"

def generate_main():
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
    settings = cea.optimization.optimization_settings.optimization_settings()

    individual = []
    lower_bound = settings.lower_bound
    upper_bound = settings.upper_bound
    continuous_variables = settings.lower_bound_conversion_technologies_shares + settings.lower_bound_solar_technologies_shares
    size = len(lower_bound)

    for i in range(size):
        print (i)
        individual.append((upper_bound[i] - lower_bound[i]) * random.random() + lower_bound[i])

    for i in range(size):
        if i < size - len(continuous_variables):
            individual[i] = int(round(individual[i]))
    print individual
    print len(continuous_variables)
    return individual




if __name__ == '__main__':
    generate_main()




