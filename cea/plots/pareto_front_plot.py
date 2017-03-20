def test_graphs_optimization():
    import cea.globalvar
    import cea.inputlocator
    import csv
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import os
    import re

    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)
    generation = 4
    os.chdir(locator.get_optimization_master_results_folder())

    with open("CheckPointcsv" + str(generation), "rb") as csv_file:
        pareto = []
        xs = []
        ys = []
        zs = []
        reader = csv.reader(csv_file)
        mydict = dict(reader)
        objective_function = mydict['objective_function_values']
        objective_function = re.findall(r'\d+\.\d+', objective_function)
        print (objective_function)
        for i in xrange(gv.initialInd):
            pareto_intermediate = [objective_function[3*i], objective_function[3*i + 1], objective_function[3*i + 2]]
            pareto.append(pareto_intermediate)
            xs.append(float(objective_function[3*i]))
            ys.append(float(objective_function[3*i + 1]))
            zs.append(float(objective_function[3*i + 2]))

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, zs, c='r', marker='o')
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        os.chdir(locator.get_optimization_plots_folder())
        plt.savefig("Generation" + str(generation) + "Pareto_Front.png")
        plt.show()


if __name__ == '__main__':
    test_graphs_optimization()
