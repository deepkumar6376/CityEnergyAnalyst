def configDesign(generation):
    import cea.globalvar
    import cea.inputlocator
    import csv
    import matplotlib
    import matplotlib.cm as cmx
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import os
    import re

    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)
    os.chdir(locator.get_optimization_master_results_folder())
    with open("CheckPoint" + str(generation), "rb") as csv_file:
        reader = csv.reader(csv_file)
        mydict = dict(reader)
        pop = mydict['population']
        m = re.findall(r"\[.*?\]", pop)
        for i in xrange(len(m)):
            m[i] = re.findall(r'\d+(?:\.\d+)?', m[i])
            m[i] = [float(j) for j in m[i]]
    ind = m[0]
    fig = plt.figure(figsize=(6,4))
    fig.suptitle('Design of the centralized heating hub')

    # Central heating plant
    subplot1 = fig.add_subplot(221, adjustable = 'box', aspect = 1)

    def NGorBG(value):
        if value%2 == 1:
            gas = 'NG'
        else:
            gas = 'BG'
        return gas

    labels = ['CC '+NGorBG(ind[0]), 'Boiler Base '+NGorBG(ind[2]), 'Boiler peak '+NGorBG(ind[4]), 'HP Lake', 'HP Sew', 'GHP']
    fracs = [ ind[2*i + 1] for i in range(6) ]
    colors = ['LimeGreen', 'LightSalmon', 'Crimson', 'RoyalBlue', 'MidnightBlue', 'Gray']

    zipper = [ (l,f,c) for (l,f,c) in zip(labels,fracs,colors) if f > 0.01 ]
    labelsPlot, fracsPlot, colorsPlot = map( list, zip(*zipper) )
    subplot1.pie(fracsPlot, labels = labelsPlot, colors = colorsPlot, startangle = 90, autopct='%1.1f%%', pctdistance = 0.5)

    # Solar total area
    subplot2 = fig.add_subplot(222, adjustable = 'box', aspect = 1)
    labels = ['Solar covered area', 'Uncovered area']
    fracs = [ ind[20], 1 - ind[20] ]
    colors = ['Gold', 'Gray']
    subplot2.pie(fracs, labels = labels, startangle = 90, colors = colors, autopct='%1.1f%%', pctdistance = 0.5)

    # Solar system distribution
    subplot3 = fig.add_subplot(223, adjustable = 'box', aspect = 1)
    labels = ['PV', 'PVT', 'SC']
    fracs = [ ind[15], ind[17], ind[19] ]
    colors = ['Yellow', 'Orange', 'OrangeRed']

    zipper = [ (l,f,c) for (l,f,c) in zip(labels,fracs,colors) if f > 0.01 ]
    labelsPlot, fracsPlot, colorsPlot = map( list, zip(*zipper) )
    subplot3.pie(fracsPlot, labels = labelsPlot, colors = colorsPlot, startangle = 90, autopct='%1.1f%%', pctdistance = 0.5)

    # Connected buildings
    connectedBuild = ind[21:].count(1) / len(ind[21:])
    subplot4 = fig.add_subplot(224, adjustable = 'box', aspect = 1)
    labels = ['Connected buildings', 'Disconnected buildings',]
    fracs = [ connectedBuild, 1 - connectedBuild]
    colors = ['Chocolate', 'Gray']
    subplot4.pie(fracs, labels = labels, startangle = 90, colors = colors, autopct='%1.1f%%', pctdistance = 0.5)
    plt.rcParams.update({'font.size':10})
    plt.show()

def test_graphs_optimization(generation):
    import cea.globalvar
    import cea.inputlocator
    import csv
    import matplotlib
    import matplotlib.cm as cmx
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
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
    if generation is 'all':
        for i in xrange(gv.NGEN):
            with open("CheckPoint" + str(i + 1), "rb") as csv_file:
                reader = csv.reader(csv_file)
                mydict = dict(reader)
                objective_function = mydict['objective_function_values']
                objective_function = re.findall(r'\d+\.\d+', objective_function)
                for j in xrange(gv.initialInd):
                    pareto_intermediate = [objective_function[3 * j], objective_function[3 * j + 1],
                                           objective_function[3 * j + 2]]
                    pareto.append(pareto_intermediate)
                    xs.append(float(objective_function[3 * j]))
                    ys.append(float(objective_function[3 * j + 1]))
                    zs.append(float(objective_function[3 * j + 2]))
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, zs, c='r', marker='o')
        ax.set_xlabel('TAC [EU/m2.yr]')
        ax.set_ylabel('CO2 [kg-CO2/m2.yr]')
        ax.set_zlabel('PEN [MJ/m2.yr]')
        os.chdir(locator.get_optimization_plots_folder())
        plt.savefig("Generation" + str(generation) + "Pareto_Front_3D.png")
        plt.show()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        cm = plt.get_cmap('jet')
        cNorm = matplotlib.colors.Normalize(vmin=min(zs), vmax=max(zs))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=50, alpha=0.8)
        ax.set_xlabel('TAC [EU/m2.yr]')
        ax.set_ylabel('CO2 [kg-CO2/m2.yr]')

        scalarMap.set_array(zs)
        fig.colorbar(scalarMap, label='PEN [MJ/m2.yr]')
        plt.grid(True)
        plt.rcParams['figure.figsize'] = (6, 4)
        plt.rcParams.update({'font.size': 12})
        plt.gcf().subplots_adjust(bottom=0.15)
        plt.savefig("Generation" + str(generation) + "Pareto_Front_2D.png")
        plt.show()
        plt.clf()

    else:
        with open("CheckPoint" + str(generation), "rb") as csv_file:
            pareto = []
            xs = []
            ys = []
            zs = []
            reader = csv.reader(csv_file)
            mydict = dict(reader)
            objective_function = mydict['objective_function_values']
            objective_function = re.findall(r'\d+\.\d+', objective_function)
            for i in xrange(gv.initialInd):
                pareto_intermediate = [objective_function[3*i], objective_function[3*i + 1], objective_function[3*i + 2]]
                pareto.append(pareto_intermediate)
                xs.append(float(objective_function[3*i]))
                ys.append(float(objective_function[3*i + 1]))
                zs.append(float(objective_function[3*i + 2]))

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(xs, ys, zs, c='r', marker='o')
            ax.set_xlabel('TAC [EU/m2.yr]')
            ax.set_ylabel('CO2 [kg-CO2/m2.yr]')
            ax.set_zlabel('PEN [MJ/m2.yr]')
            os.chdir(locator.get_optimization_plots_folder())
            plt.savefig("Generation" + str(generation) + "Pareto_Front_3D.png")
            # plt.show()

            fig = plt.figure()
            ax = fig.add_subplot(111)
            cm = plt.get_cmap('jet')
            cNorm = matplotlib.colors.Normalize(vmin=min(zs), vmax=max(zs))
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
            ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=50, alpha=0.8)
            ax.set_xlabel('TAC [EU/m2.yr]')
            ax.set_ylabel('CO2 [kg-CO2/m2.yr]')

            scalarMap.set_array(zs)
            fig.colorbar(scalarMap, label='PEN [MJ/m2.yr]')
            plt.grid(True)
            plt.rcParams['figure.figsize'] = (6, 4)
            plt.rcParams.update({'font.size': 12})
            plt.gcf().subplots_adjust(bottom=0.15)
            plt.savefig("Generation" + str(generation) + "Pareto_Front_2D.png")
            # plt.show()
            plt.clf()

def uncertainty_analysis_graphs(runs):
    import cea.globalvar
    import cea.inputlocator
    import csv
    import matplotlib
    import matplotlib.cm as cmx
    import matplotlib.pyplot as plt
    import matplotlib.pylab as plb
    from mpl_toolkits.mplot3d import Axes3D
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
        with open("CheckPointTesting_uncertainty_" + str(i), "rb") as csv_file:
            reader = csv.reader(csv_file)
            mydict = dict(reader)
            objective_function = mydict['objective_function_values']
            objective_function = re.findall(r'\d+\.\d+', objective_function)
            for j in xrange(20):
                pareto_intermediate = [objective_function[3 * j], objective_function[3 * j + 1],
                                        objective_function[3 * j + 2]]
                pareto.append(pareto_intermediate)
                xs.append(float(objective_function[3 * j]))
                ys.append(float(objective_function[3 * j + 1]))
                zs.append(float(objective_function[3 * j + 2]))
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(xs, ys, zs, c='r', marker='o')
    # ax.set_xlabel('TAC [EU/m2.yr]')
    # ax.set_ylabel('CO2 [kg-CO2/m2.yr]')
    # ax.set_zlabel('PEN [MJ/m2.yr]')
    xas = []
    yas = []
    zas = []
    with open("CheckPointFinal", "rb") as csv_file:
        reader = csv.reader(csv_file)
        mydict = dict(reader)
        objective_function = mydict['objective_function_values']
        objective_function = re.findall(r'\d+\.\d+', objective_function)
        for j in xrange(20):
            pareto_intermediate = [objective_function[3 * j], objective_function[3 * j + 1],
                                   objective_function[3 * j + 2]]
            pareto.append(pareto_intermediate)
            xas.append(float(objective_function[3 * j]))
            yas.append(float(objective_function[3 * j + 1]))
            zas.append(float(objective_function[3 * j + 2]))
    os.chdir(locator.get_optimization_plots_folder())
    # plt.savefig("Uncertainty Pareto_Front_3D.png")
    # plt.show()

    plt.figure()
    plt.subplot(111)
    plt.plot(xs,ys, 's')
    plt.subplot(111)
    plt.scatter(xas, yas, s = 400, c = 'r')
    plt.xlabel('TAC [EU/m2.yr]')
    plt.ylabel('CO2 [kg-CO2/m2.yr]')
    # plt.set_xlabel('TAC [EU/m2.yr]')
    # plt.set_ylabel('CO2 [kg-CO2/m2.yr]')
    # plt.set_zlabel('PEN [MJ/m2.yr]')
    plt.grid(True)
    plt.rcParams['figure.figsize'] = (6, 4)
    plt.rcParams.update({'font.size': 12})
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.savefig("Uncertainty.png")
    plt.show()




    fig = plt.figure()
    ax = fig.add_subplot(111)
    cm = plt.get_cmap('jet')
    cNorm = matplotlib.colors.Normalize(vmin=min(zs), vmax=max(zs))
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
    ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=50, alpha=0.8)
    ax.set_xlabel('TAC [EU/m2.yr]')
    ax.set_ylabel('CO2 [kg-CO2/m2.yr]')

    scalarMap.set_array(zs)
    fig.colorbar(scalarMap, label='PEN [MJ/m2.yr]')
    plt.grid(True)
    plt.rcParams['figure.figsize'] = (6, 4)
    plt.rcParams.update({'font.size': 12})
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.savefig("Generation Pareto_Front_2D.png")
    plt.show()
    plt.clf()

def uncertainty_analysis_statistics(runs):
    import cea.globalvar
    import cea.inputlocator
    import csv
    import numpy as np
    import matplotlib
    import matplotlib.cm as cmx
    import matplotlib.pyplot as plt
    import matplotlib.pylab as plb
    from mpl_toolkits.mplot3d import Axes3D
    import os
    import re
    import xlwt

    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)
    os.chdir(locator.get_optimization_master_results_folder())
    pareto = []
    xs = []
    ys = []
    zs = []

    for i in xrange(runs):
        with open("CheckPointTesting_uncertainty_" + str(i), "rb") as csv_file:
            reader = csv.reader(csv_file)
            mydict = dict(reader)
            objective_function = mydict['objective_function_values']
            objective_function = re.findall(r'\d+\.\d+', objective_function)
            for j in xrange(20):
                pareto_intermediate = [objective_function[3 * j], objective_function[3 * j + 1],
                                        objective_function[3 * j + 2]]
                pareto.append(pareto_intermediate)
                xs.append(float(objective_function[3 * j]))
                ys.append(float(objective_function[3 * j + 1]))
                zs.append(float(objective_function[3 * j + 2]))
    xas = []
    yas = []
    zas = []
    deviation = []
    with open("CheckPointFinal", "rb") as csv_file:
        reader = csv.reader(csv_file)
        mydict = dict(reader)
        objective_function = mydict['objective_function_values']
        objective_function = re.findall(r'\d+\.\d+', objective_function)
        for j in xrange(20):
            xas.append(float(objective_function[3 * j]))
            yas.append(float(objective_function[3 * j + 1]))
            zas.append(float(objective_function[3 * j + 2]))
    # print (xs[20:39])
    xs = np.reshape(xs,(runs,20)).T

    # with open("xs", "wb") as csv_file:
    #     writer = csv.writer(csv_file)
    #     cp = dict(population=xs)
    #     for key, value in cp.items():
    #         writer.writerow([key, value])
    #
    # with open("xas", "wb") as csv_file:
    #     writer = csv.writer(csv_file)
    #     cp = dict(population=xas)
    #     for key, value in cp.items():
    #         writer.writerow([key, value])

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
    uncertainty_analysis_statistics(100)