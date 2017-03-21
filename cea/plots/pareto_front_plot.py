def test_graphs_optimization():
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
    generation = 'all'
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
                print (objective_function)
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
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        os.chdir(locator.get_optimization_plots_folder())
        plt.savefig("Generation" + str(generation) + "Pareto_Front.png")
        plt.show()

        fig = plt.figure()
        ax = fig.add_subplot(111)
        cm = plt.get_cmap('jet')
        cNorm = matplotlib.colors.Normalize(vmin=min(zs), vmax=max(zs))
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
        ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=50, alpha=0.8)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')

        scalarMap.set_array(zs)
        fig.colorbar(scalarMap, label='Z Label')
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

            fig = plt.figure()
            ax = fig.add_subplot(111)
            cm = plt.get_cmap('jet')
            cNorm = matplotlib.colors.Normalize(vmin=min(zs), vmax=max(zs))
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=cm)
            ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=50, alpha=0.8)
            ax.set_xlabel('X Label')
            ax.set_ylabel('Y Label')

            scalarMap.set_array(zs)
            fig.colorbar(scalarMap, label='Z Label')
            plt.grid(True)
            plt.rcParams['figure.figsize'] = (6, 4)
            plt.rcParams.update({'font.size': 12})
            plt.gcf().subplots_adjust(bottom=0.15)
            plt.savefig("Generation" + str(generation) + "Pareto_Front_2D.png")
            plt.show()
            plt.clf()



if __name__ == '__main__':
    test_graphs_optimization()
