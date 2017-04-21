from __future__ import division

import matplotlib
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
import pickle
import deap
import cea.globalvar
import pandas as pd
import json
import csv
import cea.inputlocator

__author__ = "Sreepathi Bhargava Krishna"
__copyright__ = "Copyright 2017, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Sreepathi Bhargava Krishna"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"

def hourly_load_profile_plot(locator, generation, individual, week):
    """
    This function plots the hourly load profile 
    """
    # CREATE PDF FILE
    # from matplotlib.backends.backend_pdf import PdfPages
    # pdf = PdfPages(locator.get_hourly_load_profile_plots_folder())
    total_file = pd.read_csv(locator.get_total_demand()).set_index('Name')
    building_names = list(total_file.index)
    j = 0
    for i in building_names:
        a = i
        a = pd.read_csv(locator.get_demand_results_folder() + '\\' + i + '.csv')
        j = j+1





    with open(locator.get_optimization_master_results_folder() + "\CheckPoint_" + str(generation), "rb") as fp:
        data = json.load(fp)

    pop = data['population']
    ntwList = data['networkList']
    pop_individual = []
    for i in xrange(len(pop[individual])):
        if type(pop[individual][i]) is float:
            pop_individual.append(float(str(pop[individual][i])[0:4]))
        else:
            pop_individual.append(pop[individual][i])

    df = pd.read_csv(locator.get_optimization_slave_results_folder() + '\\'
                      + ''.join(str(pop_individual[i]) for i in xrange(len(pop_individual)))
                      + 'PPActivationPattern.csv')
    df['index'] = xrange(8760)

    df1 = df[(df['index'] >= week*7*24) & (df['index'] <= (week+1)*7*24)]

    fig = plt.figure()


    ax = fig.add_subplot(111)
    # ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=100, alpha=0.8, vmin=0.0, vmax=1.0)

    index = df1['index']
    ESolarProducedPVandPVT = df1['ESolarProducedPVandPVT']
    E_GHP = df1['E_GHP']
    E_PP_and_storage = df1['E_PP_and_storage']
    E_aux_HP_uncontrollable = df1['E_aux_HP_uncontrollable']
    Q_AddBoiler = df1['Q_AddBoiler']


    plt.plot(index, ESolarProducedPVandPVT, 'g')
    plt.plot(index, E_GHP, 'b')
    plt.plot(index, E_PP_and_storage, 'r')
    plt.plot(index, E_aux_HP_uncontrollable, 'o')
    plt.plot(index, Q_AddBoiler, 'c')
    plt.show()
    # pdf.savefig()

    return

if __name__ == '__main__':

    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)

    generation = 5
    individual = 1
    week = 5

    individual = individual - 1
    hourly_load_profile_plot(locator, generation, individual, week)