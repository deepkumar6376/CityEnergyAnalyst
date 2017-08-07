from __future__ import division

import matplotlib
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
import pickle
import deap
import json

__author__ = "Jimeno A. Fonseca"
__copyright__ = "Copyright 2017, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"

def frontier_2D_3OB(input_path, what_to_plot, output_path, labelx, labely, labelz,
                    show_benchmarks=True, show_fitness=True, show_in_screen=False, save_to_disc=True,
                    optimal_individual=None):
    """
    This function plots 2D scattered data of a 3 objective function
    objective 1 and 2 are plotted in the x and y axes, objective 3 is plotted as a color map

    :param input_path: path to pickle file storing the data about the front to plt
    :param what_to_plot: select between plotting "paretofrontier", "population" or "halloffame"
    :param output_path: path to save plots
    :param labelx: name of objective 1
    :param labely: name of objective 2
    :param labelz: name of objective 3
    :param show_benchmarks: Flag to show diversity benchmark on the plot
    :param show_fitness: Flag to show the
    :param show_in_screen: Flag to show plot on the screen
    :param save_to_disc:  Flag to save the plot
    :param optimal_individual: dafault None, passes data to scatter the top individual.
    :return:
    """

    #needed to
    deap.creator.create("Fitness", deap.base.Fitness, weights=(1.0, 1.0, 1.0))  # maximize shilluette and calinski
    deap.creator.create("Individual", list, fitness=deap.creator.Fitness)

    #read data form pickle file:
    cp = pickle.load(open(input_path, "rb"))
    frontier = cp[what_to_plot]
    xs, ys, zs = zip(*[ind.fitness.values for ind in frontier])
    individuals = [str(ind) for ind in frontier]

    # create figure
    fig = plt.figure()
    scalarMap = cmx.ScalarMappable(norm=matplotlib.colors.Normalize(vmin=min(zs),
                                  vmax=max(zs)), cmap=plt.get_cmap('jet'))
    scalarMap.set_array(zs)
    fig.colorbar(scalarMap, label=labelz)

    ax = fig.add_subplot(111)
    ax.scatter(xs, ys, c=scalarMap.to_rgba(zs), s=100, alpha=0.8, vmin=0.0, vmax=1.0)
    ax.set_xlabel(labelx)
    ax.set_ylabel(labely)

    #add optimal individual accoridng to multicriteria
    xs_opt, ys_opt = optimal_individual["fitness1"].values, optimal_individual["fitness2"].values
    ax.plot(xs_opt, ys_opt, marker='o', color='w', markersize=20)
    for i, txt in enumerate(optimal_individual["Individual"].values):
        ax.annotate(txt, xy=(xs_opt[i], ys_opt[i]))

    # plot optimal individual, top and bottom annotations
    len_series = len(individuals)
    if show_fitness:
        for i, txt in enumerate(individuals):
            #if xs[i] == max(xs) or xs[i] == min(xs):
            ax.annotate(txt, xy=(xs[i], ys[i]))
            #elif xs[i]==xs_opt[0] and ys[i] == ys_opt[0]:
            #    ax.annotate(optimal_individual["Individual"].values[0], xy=(xs[i], ys[i]))

    if show_benchmarks:
        #number_individuals = len(individuals)
        n_clusters_opt = str(round((1- optimal_individual["fitness2"].values[0])*365,0))
        #diversity = round(cp['diversity'], 3)
        plt.title("n'= "+n_clusters_opt)

    # get formatting
    plt.grid(True)
    plt.rcParams.update({'font.size': 24})
    plt.tight_layout()
    #plt.gcf().subplots_adjust(bottom=0.15)
    if save_to_disc:
        plt.savefig(output_path)
    if show_in_screen:
        plt.show()
    plt.close(fig)
    return

def test_graphs_optimization(generation, file_path, NGEN, save_path, pop):

    import json
    import matplotlib
    import matplotlib.cm as cmx
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import os


    os.chdir(file_path)
    xs = []
    ys = []
    zs = []
    if generation is 'all':
        for i in xrange(NGEN):
            with open("CheckPoint_" + str(i+1), "rb") as fp:
                data = json.load(fp)
                objective_function = data['population_fitness']
                print (objective_function)
                print (objective_function[1][1])
                for j in xrange(pop):
                    xs.append((objective_function[j][0]))
                    ys.append((objective_function[j][1]))
                    zs.append((objective_function[j][2]))

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(xs, ys, zs, c='r', marker='o')
        ax.set_xlabel('TAC [EU/m2.yr]')
        ax.set_ylabel('CO2 [kg-CO2/m2.yr]')
        ax.set_zlabel('PEN [MJ/m2.yr]')
        os.chdir(save_path)
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
        with open("CheckPoint_" + str(generation), "rb") as fp:
            data = json.load(fp)
            objective_function = data['population_fitness']
            print (objective_function)
            print (objective_function[1][1])
            for j in xrange(pop):
                xs.append((objective_function[j][0]))
                ys.append((objective_function[j][1]))
                zs.append((objective_function[j][2]))
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(xs, ys, zs, c='r', marker='o')
            ax.set_xlabel('TAC [EU/m2.yr]')
            ax.set_ylabel('CO2 [kg-CO2/m2.yr]')
            ax.set_zlabel('PEN [MJ/m2.yr]')
            os.chdir(save_path)
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
    return

if __name__ == '__main__':
    generation = 50  # options of 'all' or the generation number for which the plot need to be developed
    NGEN = 50  # total number of generations
    pop = 10  # total population in the generation

    # path reference to where the saved generation files are present
    file_path = r'C:\reference-case-zug\baseline\outputs\Mutation and Crossover\As usual\Run 1\data\optimization\master'
    # path reference to where the plot files need to be saved
    save_path = r'C:\reference-case-zug\baseline\outputs\Mutation and Crossover\Plots'
    test_graphs_optimization(generation, file_path, NGEN, save_path, pop)



