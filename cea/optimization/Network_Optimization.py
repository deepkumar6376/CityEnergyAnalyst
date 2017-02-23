"""
===========================
Evolutionary algorithm main
===========================

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

__author__ = "Thuy-An Nguyen"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Thuy-An Nguyen", "Tim Vollrath", "Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"

def get_thermal_network_from_shapefile(locator, network_type):
    """
    This function reads the existing node and pipe network from a shapefile and produces an edge-node incidence matrix
    (as defined by Oppelt et al., 2016) as well as the edge properties (length, start node, and end node) and node
    coordinates.

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
    :return edge_df['pipe length']: vector containing the length of each edge in the network                    (1 x e)
    :rtype edge_node_df: DataFrame
    :rtype all_nodes_df: DataFrame
    :rtype edge_df['pipe length']: array

    Side effects
    ------------
    The following files are created by this script:
        - DH_EdgeNode: csv file containing edge_node_df stored in locator.get_optimization_network_layout_folder()
        - DH_Node_DF: csv file containing all_nodes_df stored in locator.get_optimization_network_layout_folder()
        - DH_Pipe_DF: csv file containing edge_df stored in locator.get_optimization_network_layout_folder()

    ..[Oppelt, T., et al., 2016] Oppelt, T., et al. Dynamic thermo-hydraulic model of district cooling networks.
    Applied Thermal Engineering, 2016.

    """

    t0 = time.clock()

    # import shapefiles containing the network's edges and nodes
    network_edges_df = gpd.read_file(locator.get_network_layout_edges_shapefile(network_type))
    network_nodes_df = gpd.read_file(locator.get_network_layout_nodes_shapefile(network_type))

    # get node and pipe information
    node_df, edge_df = extract_network_from_shapefile(network_edges_df, network_nodes_df)

    # create consumer and plant node vectors
    node_names = node_df.index.values
    consumer_nodes = [] #np.zeros(len(node_names))#np.vstack((node_names, (node_df['consumer'] * node_df['Node']).values))
    plant_nodes = [] #np.zeros(len(node_names))#np.vstack((node_names, (node_df['plant'] * node_df['Node']).values))
    for node in node_names:
        if node_df['consumer'][node] == 1:
            consumer_nodes.append(node)
        else:
            consumer_nodes.append('')
        if node_df['plant'][node] == 1:
            plant_nodes.append(node)
        else:
            plant_nodes.append('')

    # create node catalogue indicating which nodes are plants and which consumers
    all_nodes_df = pd.DataFrame(data=[node_df['consumer'], node_df['plant']], index = ['consumer','plant'], columns = node_df.index)
    for node in all_nodes_df:
        if all_nodes_df[node]['consumer'] == 1:
            all_nodes_df[node]['consumer'] = node_df['Name'][node]
        else:
            all_nodes_df[node]['consumer'] = ''
        if all_nodes_df[node]['plant'] == 1:
            all_nodes_df[node]['plant'] = node_df['Name'][node]
        else:
            all_nodes_df[node]['plant'] = ''
    all_nodes_df.to_csv(locator.get_optimization_network_node_list_file(network_type))

    # create first edge-node matrix
    list_pipes = edge_df.index.values
    list_nodes = sorted(set(edge_df['start node']).union(set(edge_df['end node'])))
    edge_node_matrix = np.zeros((len(list_nodes), len(list_pipes)))
    for j in range(len(list_pipes)):
        for i in range(len(list_nodes)):
            if edge_df['end node'][j] == list_nodes[i]:
                edge_node_matrix[i][j] = 1
            elif edge_df['start node'][j] == list_nodes[i]:
                edge_node_matrix[i][j] = -1
    edge_node_df = pd.DataFrame(data=edge_node_matrix, index=list_nodes, columns=list_pipes)

    # Since dataframe doesn't indicate the direction of flow, an edge node matrix is generated as a first guess and
    # the mass flow at t = 0 is calculated with it. The direction of flow is then corrected by inverting negative flows.
    substation_mass_flows_df = pd.DataFrame(data = np.zeros([1,len(edge_node_df.index)]), columns = edge_node_df.index)
    total_flow = 0
    for node in consumer_nodes:
        if node != '':
            substation_mass_flows_df[node] = 1
            total_flow += 1
    for plant in plant_nodes:
        if plant != '':
            substation_mass_flows_df[plant] = -total_flow
    mass_flow_guess = calc_mass_flow_edges(edge_node_df, substation_mass_flows_df)[0]

    for i in range(len(mass_flow_guess)):
        if mass_flow_guess[i] < 0:
            mass_flow_guess[i] = abs(mass_flow_guess[i])
            edge_node_df[edge_node_df.columns[i]] = -edge_node_df[edge_node_df.columns[i]]
            new_nodes = [edge_df['end node'][i], edge_df['start node'][i]]
            edge_df['start node'][i] = new_nodes[0]
            edge_df['end node'][i] = new_nodes[1]


    edge_node_df.to_csv(locator.get_optimization_network_edge_node_matrix_file(network_type))
    edge_df.to_csv(locator.get_optimization_network_edge_list_file(network_type))

    print (time.clock() - t0, "seconds process time for Network summary\n")

    return edge_node_df, all_nodes_df, edge_df['pipe length']

def extract_network_from_shapefile(edge_shapefile_df, node_shapefile_df):
    '''
    Extracts network data into dataframes for pipes and nodes in the network

    Parameters
    ----------
    :param edge_shapefile_df: DataFrame containing all data imported from the edge shapefile
    :param node_shapefile_df: DataFrame containing all data imported from the node shapefile
    :type edge_shapefile_df: DataFrame
    :type node_shapefile_df: DataFrame

    Returns
    -------
    :return node_df: DataFrame containing all nodes and their corresponding coordinates
    :return edge_df: list of edges and their corresponding lengths and start and end nodes
    :rtype node_df: DataFrame
    :rtype edge_df: DataFrame

    '''

    import numpy as np

    # import consumer and plant nodes
    end_nodes = []
    for node in node_shapefile_df['geometry']:
        end_nodes.append(node.coords[0])
    node_shapefile_df['geometry'] = end_nodes
    node_shapefile_df['consumer'] = np.zeros(len(node_shapefile_df['Plant']))
    for node in range(len(node_shapefile_df['consumer'])):
        if node_shapefile_df['Qh'][node] > 0:
            node_shapefile_df['consumer'][node] = 1

    # create node dictionary with plant and consumer nodes
    node_dict = {}
    node_columns = ['Node', 'Name', 'plant', 'consumer', 'coordinates']
    for i in range(len(node_shapefile_df)):
        node_dict[node_shapefile_df['geometry'][i]] = ['NODE'+str(i), node_shapefile_df['Name'][i], node_shapefile_df['Plant'][i],
                                              node_shapefile_df['consumer'][i], node_shapefile_df['geometry'][i]]

    # create edge dictionary with pipe lengths and start and end nodes
    # complete node dictionary with missing nodes (i.e., joints)
    edge_dict = {}
    edge_columns = ['pipe length', 'start node', 'end node']
    pipe_nodes = []
    for j in range(len(edge_shapefile_df)):
        pipe = edge_shapefile_df['geometry'][j]
        start_node = pipe.coords[0]
        end_node = pipe.coords[len(pipe.coords)-1]
        pipe_nodes.append(pipe.coords[0])
        pipe_nodes.append(pipe.coords[len(pipe.coords)-1])
        if start_node not in node_dict.keys():
            i += 1
            node_dict[start_node] = ['NODE'+str(i), 'TEE' + str(i - len(node_shapefile_df)), 0, 0, start_node]
        if end_node not in node_dict.keys():
            i += 1
            node_dict[end_node] = ['NODE'+str(i), 'TEE' + str(i - len(node_shapefile_df)), 0, 0, end_node]
        edge_dict['EDGE' + str(j)] = [edge_shapefile_df['Shape_Leng'][j], node_dict[start_node][0], node_dict[end_node][0]]

    # # if a consumer node is not connected to the network, find the closest node and connect them with a new edge
    # # this part of the code was developed for a case in which the node and edge shapefiles were not defined consistently
    # # This has not been a problem after all, but it could eventually be a useful feature.
    # for node in node_dict:
    #     if node not in pipe_nodes:
    #         min_dist = 1000
    #         closest_node = pipe_nodes[0]
    #         for pipe_node in pipe_nodes:
    #             dist = ((node[0] - pipe_node[0])**2 + (node[1] - pipe_node[1])**2)**.5
    #             if dist < min_dist:
    #                 min_dist = dist
    #                 closest_node = pipe_node
    #         j += 1
    #         edge_dict['EDGE' + str(j)] = [min_dist, node_dict[closest_node][0], node_dict[node][0]]

    # create dataframes containing all nodes and edges
    node_df = pd.DataFrame.from_dict(node_dict, orient='index')
    node_df.columns = node_columns
    node_df = node_df.set_index(node_df['Node']).drop(['Node'], axis = 1)
    edge_df = pd.DataFrame.from_dict(edge_dict, orient='index')
    edge_df.columns = edge_columns

    return node_df, edge_df

def calc_mass_flow_edges(edge_node_df, mass_flow_substation_df):
    '''
    This function carries out the steady-state mass flow rate calculation for a predefined network with predefined mass
    flow rates at each substation based on the method from Todini et al. (1987), Ikonen et al. (2016), Oppelt et al.
    (2016), etc.

    Parameters
    ----------
    :param edge_node_df: DataFrame consisting of n rows (number of nodes) and e columns (number of edges)
                         and indicating the direction of flow of each edge e at node n: if e points to n,
                         value is 1; if e leaves node n, -1; else, 0.                                       (n x e)
    :param: mass_flow_substation_df: DataFrame containing the mass flow rate at each node n at each time
                                     of the year t                                                          (t x n)
    :type edge_node_df: DataFrame
    :type mass_flow_substation_df: DataFrame

    Return
    ------
    :return: mass_flow_edge: matrix specifying the mass flow rate at each edge e at the given time step t
    :type: mass_flow_edge: numpy.ndarray

    ..[Todini & Pilati, 1987] Todini & Pilati. "A gradient method for the analysis of pipe networks," in Computer
     Applications in Water Supply Volume 1 - Systems Analysis and Simulation, 1987.
    ..[Ikonen, E., et al, 2016] Ikonen, E., et al. Examination of Operational Optimization at Kemi District Heating Network.
    Thermal Science. 2016, Vol. 20, No.2, pp.667-678.
    ..[Oppelt, T., et al., 2016] Oppelt, T., et al. Dynamic thermo-hydraulic model of district cooling networks.
    Applied Thermal Engineering, 2016.

    '''

    # t0 = time.clock()
    mass_flow_edge = np.round(np.transpose(np.linalg.lstsq(edge_node_df.values, np.transpose(mass_flow_substation_df.values))[0]), decimals = 9)
    # print time.clock() - t0, "seconds process time for total mass flow calculation\n"

    return mass_flow_edge