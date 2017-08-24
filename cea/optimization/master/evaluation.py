"""
====================================
Evaluation function of an individual
====================================

"""
from __future__ import division

import os

import cea.optimization.master.generation as generation
import cea.optimization.master.summarize_network as nM
import numpy as np
import pandas as pd

import cea.optimization.master.cost_model as eM
import cea.optimization.preprocessing.cooling_net as coolMain
import cea.optimization.slave.slave_main as sM
import cea.optimization.supportFn as sFn
import cea.technologies.substation as sMain
import check as cCheck
from cea.optimization import slave_data


# +++++++++++++++++++++++++++++++++++++
# Main objective function evaluation
# ++++++++++++++++++++++++++++++++++++++

def evaluation_main(individual, building_names, locator, extraCosts, extraCO2, extraPrim, solar_features,
                    network_features, settings):
    """
    This function evaluates an individual

    :param individual: list with values of the individual
    :param building_names: list with names of buildings
    :param locator: locator class
    :param extraCosts: costs calculated before optimization of specific energy services
     (process heat and electricity)
    :param extraCO2: green house gas emissions calculated before optimization of specific energy services
     (process heat and electricity)
    :param extraPrim: primary energy calculated before optimization ofr specific energy services
     (process heat and electricity)
    :param solar_features: solar features call to class
    :param network_features: network features call to class
    :param gv: global variables class
    :type individual: list
    :type building_names: list
    :type locator: string
    :type extraCosts: float
    :type extraCO2: float
    :type extraPrim: float
    :type solar_features: class
    :type network_features: class
    :type gv: class
    :return: Resulting values of the objective function. costs, CO2, prim
    :rtype: tuple

    """
    # Initialize objective functions costs, CO2 and primary energy
    costs = extraCosts
    CO2 = extraCO2
    prim = extraPrim

    QUncoveredDesign = 0
    QUncoveredAnnual = 0

    # Create the string representation of the individual
    individual_barcode = sFn.individual_to_barcode(individual, settings)

    if individual_barcode.count("0") == 0:
        network_file_name = "Network_summary_result_all.csv"
    else:
        network_file_name = "Network_summary_result_" + individual_barcode + ".csv"

    if individual_barcode.count("1") > 0:
        Qheatmax = sFn.calcQmax(network_file_name, locator.get_optimization_network_results_folder())
    else:
        Qheatmax = 0

    print Qheatmax, "Qheatmax in distribution"
    Qnom = Qheatmax * (1 + settings.Qmargin_ntw)
    print (individual)
    # Modify the individual with the extra GHP constraint
    individual = cCheck.GHPCheck(individual, locator, Qnom, gv, settings)
    print (individual)

    # Export to context
    master_to_slave_vars = calc_master_to_slave_variables(individual, Qheatmax, locator, gv, settings)
    master_to_slave_vars.NETWORK_DATA_FILE = network_file_name

    if master_to_slave_vars.nBuildingsConnected > 1:
        if individual_barcode.count("0") == 0:
            master_to_slave_vars.fNameTotalCSV = locator.get_total_demand()
        else:
            master_to_slave_vars.fNameTotalCSV = os.path.join(locator.get_optimization_network_totals_folder(),
                                                              "Total_%(individual_barcode)s.csv" % locals())
    else:
        master_to_slave_vars.fNameTotalCSV = locator.get_optimization_substations_total_file(individual_barcode)

    if individual_barcode.count("1") > 0:

        print "Slave routine on", master_to_slave_vars.configKey
        (slavePrim, slaveCO2, slaveCosts, QUncoveredDesign, QUncoveredAnnual) = sM.slave_main(locator,
                                                                                              master_to_slave_vars,
                                                                                              solar_features)
        costs += slaveCosts
        CO2 += slaveCO2
        prim += slavePrim

    else:
        print "No buildings connected to distribution \n"

    print "Add extra costs"
    (addCosts, addCO2, addPrim) = eM.addCosts(individual_barcode, building_names, locator, master_to_slave_vars, QUncoveredDesign,
                                              QUncoveredAnnual, solar_features, network_features)
    print addCosts, addCO2, addPrim, "addCosts, addCO2, addPrim \n"

    if gv.ZernezFlag == 1:
        coolCosts, coolCO2, coolPrim = 0, 0, 0
    else:
        (coolCosts, coolCO2, coolPrim) = coolMain.coolingMain(locator, master_to_slave_vars.configKey, network_features,
                                                              master_to_slave_vars.WasteServersHeatRecovery)

    print coolCosts, coolCO2, coolPrim, "coolCosts, coolCO2, coolPrim \n"

    costs += addCosts + coolCosts
    CO2 += addCO2 + coolCO2
    prim += addPrim + coolPrim

    print "Evaluation of", master_to_slave_vars.configKey, "done"
    print costs, CO2, prim, " = costs, CO2, prim \n"

    return individual, costs, CO2, prim

#+++++++++++++++++++++++++++++++++++
# Boundary conditions
#+++++++++++++++++++++++++++++
def calc_master_to_slave_variables(individual, Qmax, locator, settings):
    """
    This function reads the list encoding a configuration and implements the corresponding
    for the slave routine's to use

    :param individual: list with inidividual
    :param Qmax:  peak heating demand
    :param locator: locator class
    :param gv: global variables class
    :type individual: list
    :type Qmax: float
    :type locator: string
    :type gv: class
    :return: master_to_slave_vars : class MasterSlaveVariables
    :rtype: class
    """
    # initialise class storing dynamic variables transfered from master to slave optimization
    master_to_slave_vars = slave_data.SlaveData()
    master_to_slave_vars.configKey = "".join(str(e)[0:4] for e in individual)
    
    individual_barcode = sFn.individual_to_barcode(individual, settings)
    master_to_slave_vars.nBuildingsConnected = individual_barcode.count("1") # counting the number of buildings connected
    
    Qnom = Qmax * (1 + settings.Qmargin_ntw)
    discrete_variables = settings.discrete_variables
    
    # Heating systems
    
    #CHP units with NG & furnace with biomass wet
    if individual[0] == 1 or individual[0] == 3:
        if gv.Furnace_allowed == 1:
            master_to_slave_vars.Furnace_on = 1
            master_to_slave_vars.Furnace_Q_max = max(individual[discrete_variables + 0] * Qnom, settings.QminShare * Qnom)
            print master_to_slave_vars.Furnace_Q_max, "Furnace wet"
            master_to_slave_vars.Furn_Moist_type = "wet"
        elif gv.CC_allowed == 1:
            master_to_slave_vars.CC_on = 1
            master_to_slave_vars.CC_GT_SIZE = max(individual[discrete_variables + 0] * Qnom * 1.3, settings.QminShare * Qnom * 1.3)
            #1.3 is the conversion factor between the GT_Elec_size NG and Q_DHN
            print master_to_slave_vars.CC_GT_SIZE, "CC NG"
            master_to_slave_vars.gt_fuel = "NG"
     
    #CHP units with BG& furnace with biomass dry       
    if individual[0] == 2 or individual[0] == 4:
        if gv.Furnace_allowed == 1:
            master_to_slave_vars.Furnace_on = 1
            master_to_slave_vars.Furnace_Q_max = max(individual[discrete_variables + 0] * Qnom, settings.QminShare * Qnom)
            print master_to_slave_vars.Furnace_Q_max, "Furnace dry"
            master_to_slave_vars.Furn_Moist_type = "dry"
        elif gv.CC_allowed == 1:
            master_to_slave_vars.CC_on = 1
            master_to_slave_vars.CC_GT_SIZE = max(individual[discrete_variables + 0] * Qnom * 1.5, settings.QminShare * Qnom * 1.5)
            #1.5 is the conversion factor between the GT_Elec_size BG and Q_DHN
            print master_to_slave_vars.CC_GT_SIZE, "CC BG"
            master_to_slave_vars.gt_fuel = "BG"

    # Base boiler NG 
    if individual[1] == 1:
        master_to_slave_vars.Boiler_on = 1
        master_to_slave_vars.Boiler_Q_max = max(individual[discrete_variables + 1] * Qnom, settings.QminShare * Qnom)
        print master_to_slave_vars.Boiler_Q_max, "Boiler base NG"
        master_to_slave_vars.BoilerType = "NG"
    
    # Base boiler BG    
    if individual[1] == 2:
        master_to_slave_vars.Boiler_on = 1
        master_to_slave_vars.Boiler_Q_max = max(individual[discrete_variables + 1] * Qnom, settings.QminShare * Qnom)
        print master_to_slave_vars.Boiler_Q_max, "Boiler base BG"
        master_to_slave_vars.BoilerType = "BG"
    
    # peak boiler NG         
    if individual[2] == 1:
        master_to_slave_vars.BoilerPeak_on = 1
        master_to_slave_vars.BoilerPeak_Q_max = max(individual[discrete_variables + 2] * Qnom, settings.QminShare * Qnom)
        print master_to_slave_vars.BoilerPeak_Q_max, "Boiler peak NG"
        master_to_slave_vars.BoilerPeakType = "NG"
    
    # peak boiler BG   
    if individual[2] == 2:
        master_to_slave_vars.BoilerPeak_on = 1
        master_to_slave_vars.BoilerPeak_Q_max = max(individual[discrete_variables + 2] * Qnom, settings.QminShare * Qnom)
        print master_to_slave_vars.BoilerPeak_Q_max, "Boiler peak BG"
        master_to_slave_vars.BoilerPeakType = "BG"
    
    # lake - heat pump
    if individual[3] == 1  and gv.HPLake_allowed == 1:
        master_to_slave_vars.HP_Lake_on = 1
        master_to_slave_vars.HPLake_maxSize = max(individual[discrete_variables + 3] * Qnom, settings.QminShare * Qnom)
        print master_to_slave_vars.HPLake_maxSize, "Lake"
    
    # sewage - heatpump    
    if individual[4] == 1 and gv.HPSew_allowed == 1:
        master_to_slave_vars.HP_Sew_on = 1
        master_to_slave_vars.HPSew_maxSize = max(individual[discrete_variables + 4] * Qnom, settings.QminShare * Qnom)
        print master_to_slave_vars.HPSew_maxSize, "Sewage"
    
    # Gwound source- heatpump
    if individual[5] == 1 and gv.GHP_allowed == 1:
        master_to_slave_vars.GHP_on = 1
        GHP_Qmax = max(individual[discrete_variables + 5] * Qnom, settings.QminShare * Qnom)
        master_to_slave_vars.GHP_number = GHP_Qmax / gv.GHP_HmaxSize
        print GHP_Qmax, "GHP"
    
    # heat recovery servers and compresor
    irank = settings.nHeat
    master_to_slave_vars.WasteServersHeatRecovery = individual[irank]
    master_to_slave_vars.WasteCompressorHeatRecovery = individual[irank + 1]
    
    # Solar systems
    roof_area = np.array(pd.read_csv(locator.get_total_demand(), usecols=["Aroof_m2"]))
    
    areaAvail = 0
    totalArea = 0
    for i in range( len(individual_barcode) ):
        index = individual_barcode[i]
        if index == "1":
            areaAvail += roof_area[i][0]
        totalArea += roof_area[i][0]

    shareAvail = areaAvail / totalArea
    solar_share_index = discrete_variables + settings.nHeat
    
    irank = settings.nHeat + settings.nHR
    master_to_slave_vars.SOLAR_PART_PV = max(individual[irank] * individual[solar_share_index] * individual[solar_share_index+3] * shareAvail,0)
    print master_to_slave_vars.SOLAR_PART_PV, "PV"
    master_to_slave_vars.SOLAR_PART_PVT = max(individual[irank + 1] * individual[solar_share_index + 1] * individual[solar_share_index+3] * shareAvail,0)
    print master_to_slave_vars.SOLAR_PART_PVT, "PVT"
    master_to_slave_vars.SOLAR_PART_SC = max(individual[irank + 2] * individual[solar_share_index + 2] * individual[solar_share_index+3] * shareAvail,0)
    print master_to_slave_vars.SOLAR_PART_SC, "SC"
    
    return master_to_slave_vars


def checkNtw(individual, ntwList, locator, settings):
    """
    This function calls the distribution routine if necessary
    
    :param individual: network configuration considered
    :param ntwList: list of DHN configurations previously encounterd in the master
    :param locator: path to the folder
    :type individual: list
    :type ntwList: list
    :type locator: string
    :return: None
    :rtype: Nonetype
    """
    indCombi = sFn.individual_to_barcode(individual, settings)
    print indCombi,2
    
    if not (indCombi in ntwList) and indCombi.count("1") > 0:
        ntwList.append(indCombi)
        
        if indCombi.count("1") == 1:
            total_demand = pd.read_csv(
                os.path.join(locator.get_optimization_network_results_folder(), "Total_%(indCombi)s.csv" % locals()))
            building_names = total_demand.Name.values
            print "Direct launch of distribution summary routine for", indCombi
            nM.network_main(locator, total_demand, building_names, gv, indCombi)

        else:
            total_demand = sFn.createTotalNtwCsv(indCombi, locator)
            building_names = total_demand.Name.values

            # Run the substation and distribution routines
            print "Re-run the substation routine for new distribution configuration", indCombi
            sMain.substation_main(locator, total_demand, building_names, settings, indCombi )
            
            print "Launch distribution summary routine"
            nM.network_main(locator, total_demand, building_names, indCombi)


def epsIndicator(frontOld, frontNew):
    """
    This function computes the epsilon indicator
    
    :param frontOld: Old Pareto front
    :param frontNew: New Pareto front
    :type frontOld: list
    :type frontNew:list
    :return: epsilon indicator between the old and new Pareto fronts
    :rtype: float
    """
    epsInd = 0
    firstValueAll = True
    
    for indNew in frontNew:
        tempEpsInd = 0
        firstValue = True
        
        for indOld in frontOld:
            (aOld, bOld, cOld) = indOld.fitness.values
            (aNew, bNew, cNew) = indNew.fitness.values
            compare = max(aOld-aNew, bOld-bNew, cOld-cNew)
            
            if firstValue:
                tempEpsInd = compare
                firstValue = False
            
            if compare < tempEpsInd:
                tempEpsInd = compare
        
        if firstValueAll:
            epsInd = tempEpsInd
            firstValueAll = False
            
        if tempEpsInd > epsInd:
            epsInd = tempEpsInd
            
    return epsInd










