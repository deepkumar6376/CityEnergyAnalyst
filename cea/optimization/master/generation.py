"""
==================
Create individuals
==================

"""
from __future__ import division
import random
import numpy as np, numpy.random
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
    individual_size = len(lower_bound)

    for i in range(individual_size):
        individual.append((upper_bound[i] - lower_bound[i]) * random.random() + lower_bound[i])

    for i in range(individual_size):
        if i < individual_size - len(continuous_variables):
            individual[i] = int(round(individual[i]))

    sum_conversion_technologies_shares = 0
    sum_solar_technologies_share = 0

    # adjusting conversion technologies shares to be less than or equal to 1
    for i in range(len(settings.lower_bound_conversion_technologies_shares)):
        sum_conversion_technologies_shares += individual[individual_size - len(continuous_variables) + i]

    if sum_conversion_technologies_shares > 1: # if the sum of shares is greater than 1, we reset it randomly to be equal to 1
        conversion_technologies_share_random_generation = np.random.dirichlet(np.ones(len(settings.lower_bound_conversion_technologies_shares)), size = 1)
        for i in range(len(settings.lower_bound_conversion_technologies_shares)):
            individual[individual_size - len(continuous_variables) + i] = conversion_technologies_share_random_generation[0][i]

    # adjusting solar technologies share to be less than or equal to 1
    for i in range(len(settings.lower_bound_solar_technologies_shares)):
        sum_solar_technologies_share += individual[individual_size - len(continuous_variables) +  len(settings.lower_bound_conversion_technologies_shares) + i]

    if sum_solar_technologies_share > 1: # if the sum of shares is greater than 1, we reset it randomly to be equal to 1
        # Solar technologies lower bound has three technologies and the final variable corresponds to share on overall area available
        solar_technologies_share_random_generation = np.random.dirichlet(np.ones(len(settings.lower_bound_solar_technologies_shares) - 1), size = 1)
        for i in range(len(settings.lower_bound_solar_technologies_shares) - 1):
            individual[individual_size - len(continuous_variables) + 1 + (len(settings.lower_bound_conversion_technologies_shares) - 1) + i] = solar_technologies_share_random_generation[0][i]

    return individual

if __name__ == '__main__':
    generate_main()




