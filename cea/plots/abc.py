def uncertainty_analysis_statistics(runs):
    import cea.globalvar
    import cea.inputlocator
    import csv
    import json
    import numpy as np
    import os
    import re
    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)
    os.chdir(locator.get_optimization_master_results_folder())
    pareto = []
    xs = []
    ys = []
    zs = []

    for i in xrange(runs):
        with open("CheckPointTesting_uncertainty_" + str(i), "rb") as fp:
            data = json.load(fp)
            objective_function = data['population_fitness']
            print (objective_function[0][0])
            print (objective_function[0][1])
            print (objective_function[0][2])

            for i in xrange(20):
                xs.append(objective_function[i][0])
                ys.append(objective_function[i][1])
                zs.append(objective_function[i][2])

    xas = []
    yas = []
    zas = []
    deviation = []
    with open("CheckPointFinal", "rb") as fp:
        data = json.load(fp)
        objective_function = data['population_fitness']
        print (objective_function[0][0])
        print (objective_function[0][1])
        print (objective_function[0][2])

        for i in xrange(20):
            xas.append(objective_function[i][0])
            yas.append(objective_function[i][1])
            zas.append(objective_function[i][2])
    # xs = np.reshape(xs,(runs,20)).T

    with open("xs_j", "wb") as fp:
        cp = dict(objective = xs)
        json.dump(cp,fp)

    with open("xs", "wb") as csv_file:
        writer = csv.writer(csv_file)
        cp = dict(population=xs)
        for key, value in cp.items():
            writer.writerow([key, value])

    with open("xas", "wb") as csv_file:
        writer = csv.writer(csv_file)
        cp = dict(population=xas)
        for key, value in cp.items():
            writer.writerow([key, value])

    print (xs[0][1])
    print (xs[1][1])
    print (len(xs[0]))
    for i in xrange(100):
        for j in xrange(20):
            # print (xs[j][i])
            print (xas[j])
            dev = (abs(xs[j][i] - xas[j])/ xas[j]) * 100
            # print (dev)
            deviation.append(dev)
    print (len(deviation))
    print (deviation[0:19])
    print (abs(xs[0][0] - xas[0])*100/xas[0])
    # a = np.array(deviation)
    # np.reshape(a, (20,100))
    print (deviation)
    with open("dev", "wb") as csv_file:
        writer = csv.writer(csv_file)
        cp = dict(population=deviation)
        for key, value in cp.items():
            writer.writerow([key, value])



    os.chdir(locator.get_optimization_plots_folder())
    # plt.savefig("Uncertainty Pareto_Front_3D.png")
    # plt.show()





if __name__ == '__main__':
    generation = 'all'
    # configDesign(generation)
    # test_graphs_optimization(generation)
    # uncertainty_analysis_graphs(100)
    uncertainty_analysis_statistics(500)
