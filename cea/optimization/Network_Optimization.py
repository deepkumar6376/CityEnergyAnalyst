from __future__ import print_function

"""
============================
Hydraulic - thermal network
============================

"""
from __future__ import division
import time
import numpy as np
import pandas as pd
from cea.technologies.substation import substation_main
import cea.technologies.substation_matrix as substation
import math
import cea.globalvar as gv
from cea.utilities import epwreader
from cea.resources import geothermal
import os
from scipy.linalg import block_diag
import scipy
import geopandas as gpd


__author__ = "Martin Mosteiro Romero, Shanshan Hsieh"
__copyright__ = "Copyright 2016, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Martin Mosteiro Romero", "Shanshan Hsieh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"

def get_thermal_network_from_csv(locator, network_type):
    """
    This function reads the existing node and pipe network from csv files (as provided for the Zug reference case) and
    produces an edge-node incidence matrix (as defined by Oppelt et al., 2016) as well as the length of each edge.

    Parameters
    ----------
    :param locator: an InputLocator instance set to the scenario to work on
    :param network_type: a string that defines whether the network is a district heating ('DH') or cooling ('DC')
                         network
    :type locator: InputLocator
    :type network_type: str

    Returns
    -------
    :return edge_node_df: DataFrame consisting of n rows (number of nodes) and e columns (number of edges) and
                        indicating direction of flow of each edge e at node n: if e points to n, value is 1; if
                        e leaves node n, -1; else, 0.                                                           (n x e)
    :return all_nodes_df: DataFrame that contains all nodes, whether a node is a consumer, plant, or neither,
                        and, if it is a consumer or plant, the name of the corresponding building               (2 x n)
    :return pipe_data_df['LENGTH']: vector containing the length of each edge in the network                    (1 x e)
    :rtype edge_node_df: DataFrame
    :rtype all_nodes_df: DataFrame
    :rtype pipe_data_df['LENGTH']: array

    Side effects
    ------------
    The following files are created by this script:
        - DH_EdgeNode: csv file containing edge_node_df stored in locator.get_optimization_network_layout_folder()
        - DH_AllNodes: csv file containing all_nodes_df stored in locator.get_optimization_network_layout_folder()

    ..[Oppelt, T., et al., 2016] Oppelt, T., et al. Dynamic thermo-hydraulic model of district cooling networks.
    Applied Thermal Engineering, 2016.

    """

    t0 = time.clock()

    # get node and pipe data
    node_data_df = pd.read_csv(locator.get_network_layout_nodes_csv_file(network_type))
    pipe_data_df = pd.read_csv(locator.get_network_layout_pipes_csv_file(network_type))

    # create consumer and plant node vectors from node data
    for column in ['Plant','Sink']:
        if type(node_data_df[column][0]) != int:
           node_data_df[column] = node_data_df[column].astype(int)
    node_names = node_data_df['DC_ID'].values
    consumer_nodes = np.vstack((node_names,(node_data_df['Sink']*node_data_df['Name']).values))
    plant_nodes = np.vstack((node_names,(node_data_df['Plant']*node_data_df['Name']).values))

    # create edge-node matrix from pipe data
    pipe_data_df = pipe_data_df.set_index(pipe_data_df['DC_ID'].values, drop=True)
    list_pipes = pipe_data_df['DC_ID']
    list_nodes = sorted(set(pipe_data_df['NODE1']).union(set(pipe_data_df['NODE2'])))
    edge_node_matrix = np.zeros((len(list_nodes),len(list_pipes)))
    for j in range(len(list_pipes)):
        for i in range(len(list_nodes)):
            if pipe_data_df['NODE2'][j] == list_nodes[i]:
                edge_node_matrix[i][j] = 1
            elif pipe_data_df['NODE1'][j] == list_nodes[i]:
                edge_node_matrix[i][j] = -1
    edge_node_df = pd.DataFrame(data=edge_node_matrix, index = list_nodes, columns = list_pipes)

    edge_node_df.to_csv(locator.get_optimization_network_edge_node_matrix_file(network_type))
    all_nodes_df = pd.DataFrame(data=[consumer_nodes[1][:], plant_nodes[1][:]], index = ['consumer','plant'], columns = consumer_nodes[0][:])
    all_nodes_df = all_nodes_df[edge_node_df.index.tolist()]
    all_nodes_df.to_csv(locator.get_optimization_network_node_list_file(network_type))

    print (time.clock() - t0, "seconds process time for Network summary\n")

    return edge_node_df, all_nodes_df, pipe_data_df['LENGTH']

def run_as_script(scenario_path=None):
    """
    run the whole network summary routine
    """
    import cea.globalvar
    import cea.inputlocator as inputlocator
    from geopandas import GeoDataFrame as gpdf
    from cea.utilities import epwreader
    from cea.resources import geothermal

    gv = cea.globalvar.GlobalVariables()

    if scenario_path is None:
        scenario_path = gv.scenario_reference

    locator = inputlocator.InputLocator(scenario_path=scenario_path)
    weather_file = locator.get_default_weather()

    # add geothermal part of preprocessing
    T_ambient = epwreader.epw_reader(weather_file)['drybulb_C']
    gv.ground_temperature = geothermal.calc_ground_temperature(T_ambient.values, gv)

    # add options for data sources: heating or cooling network, csv or shapefile
    network_type = ['DH', 'DC'] # set to either 'DH' or 'DC'
    source = ['csv', 'shapefile'] # set to csv or shapefile

    get_thermal_network_from_csv(locator, network_type[0])
    print ('test thermal_network_main() succeeded')

if __name__ == '__main__':
    run_as_script()