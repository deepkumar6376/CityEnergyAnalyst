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

    print edge_node_df, all_nodes_df

    return edge_node_df, all_nodes_df, edge_df['pipe length']

def extract_network_from_shapefile(edge_shapefile_df, node_shapefile_df):

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

    # create dataframes containing all nodes and edges
    node_df = pd.DataFrame.from_dict(node_dict, orient='index')
    node_df.columns = node_columns
    node_df = node_df.set_index(node_df['Node']).drop(['Node'], axis = 1)
    edge_df = pd.DataFrame.from_dict(edge_dict, orient='index')
    edge_df.columns = edge_columns

    return node_df, edge_df

def calc_mass_flow_edges(edge_node_df, mass_flow_substation_df):

    # t0 = time.clock()
    mass_flow_edge = np.round(np.transpose(np.linalg.lstsq(edge_node_df.values, np.transpose(mass_flow_substation_df.values))[0]), decimals = 9)
    # print time.clock() - t0, "seconds process time for total mass flow calculation\n"

    return mass_flow_edge

def run_as_script(scenario_path=None):
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
    source = ['shapefile'] # set to csv or shapefile

    get_thermal_network_from_shapefile(locator, network_type)
    print ('test thermal_network_main() succeeded')

if __name__ == '__main__':
    run_as_script()