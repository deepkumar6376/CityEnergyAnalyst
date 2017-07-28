from __future__ import division

import matplotlib
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
import pickle
import deap
import cea.globalvar
import pandas as pd
import numpy as np
import json
import os
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

def load_profile_plot(locator, generation, individual, week, yearly):
    """
    This function plots the hourly load profile
    """
    # CREATE PDF FILE
    # from matplotlib.backends.backend_pdf import PdfPages
    # pdf = PdfPages(locator.get_hourly_load_profile_plots_folder())
    total_file = pd.read_csv(locator.get_total_demand()).set_index('Name')
    building_names = list(total_file.index)
    building_total = pd.DataFrame(np.zeros((8760,4)), columns=['QEf_kWh', 'QHf_kWh', 'QCf_kWh', 'Ef_kWh'])
    for i in xrange(len(building_names)):
        building_demand_results = 'building' + str(i)
        building_demand_results = pd.read_csv(locator.get_demand_results_folder() + '\\' + building_names[i] + '.csv')
        for name in ['QEf_kWh', 'QHf_kWh', 'QCf_kWh', 'Ef_kWh']:
            building_total[name] = building_total[name] + building_demand_results[name]

    print (building_total['QEf_kWh'])
    building_total['index'] = xrange(8760)

    with open(locator.get_optimization_master_results_folder() + "\CheckPoint_" + str(generation), "rb") as fp:
        data = json.load(fp)

    pop = data['population']
    ntwList = data['networkList']
    pop_individual = []
    for i in xrange(len(pop[individual])):
        if type(pop[individual][i]) is float:
            pop_individual.append((str(pop[individual][i])[0:4]))
        else:
            pop_individual.append(pop[individual][i])

    df_PPA = pd.read_csv((locator.get_optimization_slave_results_folder() + '\\' \
           + ''.join(str(pop_individual[i]) for i in xrange(len(pop_individual))) \
           + '_PPActivationPattern.csv'))
    df_PPA['index'] = xrange(8760)

    df_SO = pd.read_csv((locator.get_optimization_slave_results_folder() + '\\' \
           + ''.join(str(pop_individual[i]) for i in xrange(len(pop_individual))) \
           + '_StorageOperationData.csv'))
    df_SO['index'] = xrange(8760)
    index = df_PPA['index']

    #  yearly

    network_demand = df_SO['Q_DH_networkload_W']
    Q_from_storage = df_SO['Q_DH_networkload_W'] - df_SO['Q_missing_W']
    Q_from_base_boiler = df_PPA['Q_BoilerBase_W']
    Q_from_peak_boiler = df_PPA['Q_BoilerPeak_W']
    Q_from_additional_boiler = df_PPA['Q_AddBoiler_W']
    Q_from_CC = df_PPA['Q_CC_W']
    Q_from_furnace = df_PPA['Q_Furnace_W']
    Q_from_GHP = df_PPA['Q_GHP_W']
    Q_from_lake = df_PPA['Q_HPLake_W']
    Q_from_sewage = df_PPA['Q_HPSew_W']
    Q_from_PV = df_SO['Q_SCandPVT_gen_Wh']

    

    # plt.plot(index, network_demand, 'r')
    # plt.plot(index, Q_from_storage, 'b')
    # plt.plot(index, Q_from_base_boiler + Q_from_peak_boiler + Q_from_additional_boiler, 'm')
    # plt.plot(index, Q_from_GHP, 'g')
    # plt.plot(index, Q_from_lake, 'y')
    # plt.plot(index, Q_from_sewage, 'k')
    plt.subplot(2, 1, 1)
    plt.plot([], [], color='b', label='Q_from_storage', linewidth=5)
    plt.plot([], [], color='tab:orange', label='Q_from_PV', linewidth=5)
    plt.plot([], [], color='c', label='Q_from_boiler', linewidth=5)
    plt.plot([], [], color='m', label='Q_from_CC', linewidth=5)
    plt.plot([], [], color='y', label='Q_from_furnace', linewidth=5)
    plt.plot([], [], color='k', label='Q_from_GHP', linewidth=5)
    plt.plot([], [], color='r', label='Q_from_lake', linewidth=5)
    plt.plot([], [], color='g', label='Q_from_sewage', linewidth=5)


    plt.stackplot(index, Q_from_storage, Q_from_PV, Q_from_additional_boiler + Q_from_base_boiler + Q_from_peak_boiler,
                  Q_from_CC, Q_from_furnace, Q_from_GHP, Q_from_lake, Q_from_sewage,
                  colors=['b', 'tab:orange', 'c', 'm', 'y', 'k', 'r', 'g'])

    plt.xlabel('hour number')
    plt.ylabel('Thermal Energy in W')
    plt.legend()
    plt.show()
    # testing

    #  electricity



    plt.subplot(2, 1, 2)


    #  weekly

    df1_PPA = df_PPA[(df_PPA['index'] >= week * 7 * 24) & (df_PPA['index'] <= (week + 1) * 7 * 24)]
    df1_SO = df_SO[(df_SO['index'] >= week * 7 * 24) & (df_SO['index'] <= (week + 1) * 7 * 24)]
    index = df1_PPA['index']

    network_demand = df1_SO['Q_DH_networkload_W']
    Q_from_storage = df1_SO['Q_DH_networkload_W'] - df1_SO['Q_missing_W']
    Q_from_base_boiler = df1_PPA['Q_BoilerBase_W']
    Q_from_peak_boiler = df1_PPA['Q_BoilerPeak_W']
    Q_from_additional_boiler = df1_PPA['Q_AddBoiler_W']
    Q_from_CC = df1_PPA['Q_CC_W']
    Q_from_furnace = df1_PPA['Q_Furnace_W']
    Q_from_GHP = df1_PPA['Q_GHP_W']
    Q_from_lake = df1_PPA['Q_HPLake_W']
    Q_from_sewage = df1_PPA['Q_HPSew_W']

    fig, ax = plt.subplots()


    plt.plot([], [], color='b', label='Q_from_storage', linewidth=5)
    plt.plot([], [], color='c', label='Q_from_boiler', linewidth=5)
    plt.plot([], [], color='m', label='Q_from_CC', linewidth=5)
    plt.plot([], [], color='y', label='Q_from_furnace', linewidth=5)
    plt.plot([], [], color='k', label='Q_from_GHP', linewidth=5)
    plt.plot([], [], color='r', label='Q_from_lake', linewidth=5)
    plt.plot([], [], color='g', label='Q_from_sewage', linewidth=5)

    plt.stackplot (index, Q_from_storage, Q_from_additional_boiler + Q_from_base_boiler + Q_from_peak_boiler,
                  Q_from_CC, Q_from_furnace, Q_from_GHP, Q_from_lake, Q_from_sewage, colors = ['b', 'c', 'm', 'y', 'k', 'r', 'g'])

    plt.xlabel('hour number')
    plt.ylabel('Thermal Energy in W')
    plt.legend()
    plt.show()
    print (''.join(str(pop_individual[i]) for i in xrange(len(pop_individual))))


    return

if __name__ == '__main__':

    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)

    generation = 5
    individual = 5
    yearly = True
    week = 2

    individual = individual - 1
    load_profile_plot(locator, generation, individual, week, yearly)