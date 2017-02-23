"""
===========================
Evolutionary algorithm main
===========================

"""
from __future__ import division

import os
import time
from pickle import Pickler, Unpickler

import cea.optimization.conversion_storage.master.evaluation as evaluation_function
import cea.optimization.conversion_storage.master.generation as generation_function
import mutations as mut
import selection as sel
from deap import base
from deap import creator
from deap import tools

import cea.optimization.conversion_storage.master.crossover as cx

__author__ = "Thuy-An Nguyen"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Thuy-An Nguyen", "Tim Vollrath", "Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"


def evolutionary_algo_main(locator, building_names, extra_costs, extra_CO2, extra_primary_energy, solar_features,
                           network_features, gv, genCP=0):
    """
    Evolutionary algorithm to optimize the district energy system's design.
    This algortihm optimizes the size and operation of technologies for a district heating netowrk.
    electrical netowrk are not considered but their burdens in terms electricity costs, efficiency and emissions
    is added on top of the optimization
    The equipment for Cooling networks is not optimized as it is assumed that all customer with cooling needs will be
    connected to a lake. in case there is not enough cvapacity form the lake a chiller and cooling tower is used to cover
    the extra needs.

    :param locator: locator class
    :param building_names: vector with building names
    :param extra_costs: costs calculated before optimization of specific energy services
     (process heat and electricity)
    :param extra_CO2: green house gas emissions calculated before optimization of specific energy services
     (process heat and electricity)
    :param extra_primary_energy: primary energy calculated before optimization of specific energy services
     (process heat and electricity)
    :param solar_features: object class with vectors and values of interest for the integration of solar potentials
    :param network_features: object class with linear coefficients of the network obtained after its optimization
    :param gv: global variables class
    :param genCP: 0
    :type locator: class
    :type building_names: array
    :type extra_costs: float
    :type extra_CO2: float
    :type extra_primary_energy: float
    :type solar_features: class
    :type network_features: class
    :type gv: class
    :type genCP: int
    :return: for every generation 'g': it stores the results of every generation of the genetic algorithm in the
     subfolders locator.get_optimization_master_results_folder() as a python pickle file.
    :rtype: pickled file
    """
    t0 = time.clock()

    # get number of buildings
    nBuildings = len(building_names)

    # DEFINE OBJECTIVE FUNCTION
    def objective_function(ind):
        (costs, CO2, prim) = evaluation_function.evaluation_main(ind, building_names, locator, extra_costs, extra_CO2,
                                                                 extra_primary_energy, solar_features,
                                                                 network_features, gv)
        return (costs, CO2, prim)

    # SET-UP EVOLUTIONARY ALGORITHM
    # Contains 3 minimization objectives : Costs, CO2 emissions, Primary Energy Needs
    creator.create("Fitness", base.Fitness, weights=(-1.0, -1.0, -1.0))
    creator.create("Individual", list, fitness=creator.Fitness)
    toolbox = base.Toolbox()
    toolbox.register("generate", generation_function.generate_main, nBuildings, gv)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.generate)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", objective_function)

    ntwList = ["1" * nBuildings]
    epsInd = []
    invalid_ind = []

    return 1




