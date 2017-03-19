def test_graphs_optimization():
    import cea.globalvar
    import cea.inputlocator
    import csv
    import matplotlib.pyplot as plt

    import os
    import re

    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)
    generation = 1
    os.chdir(locator.get_optimization_master_results_folder())

    with open("CheckPointcsv" + str(generation), "rb") as csv_file:
        pareto = []
        reader = csv.reader(csv_file)
        mydict = dict(reader)
        objective_function = mydict['objective_function_values']
        objective_function = re.findall(r'\d+\.\d+', objective_function)
        print (objective_function)
        for i in xrange(gv.initialInd):
            pareto_intermediate = [objective_function[3*i], objective_function[3*i + 1], objective_function[3*i + 2]]
            pareto.append(pareto_intermediate)

        print (pareto)







if __name__ == '__main__':
    test_graphs_optimization()
