import pandas as pd
import os
from cea.demand.calibration.clustering.clustering_main import clustering_main, optimization_clustering_main
import cea.globalvar as gv
import cea.inputlocator as inputlocator
import seaborn
import matplotlib.pyplot as plt
from cea.analysis.mcda import mcda_cluster_main



# Local variables
gv = gv.GlobalVariables()
scenario_path = gv.scenario_reference
locator = inputlocator.InputLocator(scenario_path=scenario_path)
data_folder_path = r'C:\Users\Jimeno\Desktop\data'
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']

wanna_optimize = True # if False it gets the minimum number of clusters.

for day in days:
    output_file1= 'type_restaurant_Singapore_' + day + 'box_plot.png'
    output_file2 = 'type_restaurant_Singapore_' + day + 'cluster.png'
    output_path1 = os.path.join(locator.get_calibration_clustering_plots_folder(), output_file1)
    output_path2 = os.path.join(locator.get_calibration_clustering_plots_folder(), output_file2)
    data = pd.read_csv(os.path.join(data_folder_path, 'type_restaurant_Singapore_' + day + '.csv'))
    columns = [str(x) for x in range(24)]
    data_matrix = data.as_matrix(columns=columns)

    if wanna_optimize:
        start_generation = None  # or the number of generation to start from
        number_individuals = 16
        number_generations = 10
        optimization_clustering_main(locator=locator, data=data_matrix, start_generation=start_generation,
                                     number_individuals=number_individuals, number_generations=number_generations,
                                     building_name=day, gv=gv)

        generation = number_generations
        weight_fitness1 = 100  # accurracy
        weight_fitness2 = 200  # complexity
        weight_fitness3 = 80  # compression
        what_to_plot = "paretofrontier"
        output_path = locator.get_calibration_cluster_mcda(generation)

        # read_checkpoint
        input_path = locator.get_calibration_cluster_opt_checkpoint(generation, day)
        result = mcda_cluster_main(input_path=input_path, what_to_plot=what_to_plot,
                                   weight_fitness1=weight_fitness1, weight_fitness2=weight_fitness2,
                                   weight_fitness3=weight_fitness3)
        result["name"] = day
        result_final = pd.DataFrame(result).T['Individual'].values[0]

        word_size = result_final[0]
        alphabet_size = result_final[1]
    else:
        word_size = 3
        alphabet_size = 4

    a = data_matrix.flatten()
    ts = pd.Series(a, index=pd.date_range(start="2014-02-01", periods=len(a), freq="H"))
    fig, ax = plt.subplots(figsize=(12, 5))
    labelx = "Hour of the day"
    labely = "frequency [%]"
    ax.set_xlabel(labelx)
    ax.set_ylabel(labely)
    ax.set_title(day)
    ax.set_ylim([0,100])
    seaborn.boxplot(ts.index.hour, ts, ax=ax)
    plt.rcParams.update({'font.size': 14})
    plt.tight_layout()
    plt.savefig(output_path1)
    plt.close(fig)

    # calculate sax for timesieries data

    clustering_main(locator=locator, data=data_matrix, word_size=word_size, alphabet_size=alphabet_size)
    #plot
    show_benchmark = False
    save_to_disc = True
    show_in_screen = False
    show_legend = False

    input_path = locator.get_calibration_cluster('clusters_mean')
    data = pd.read_csv(input_path)

    #create figure
    fig = plt.figure(figsize=(12, 5))
    ax = data.plot(grid=True, legend=show_legend)
    ax.set_xlabel(labelx)
    ax.set_ylabel(labely)
    ax.set_title(day)
    ax.set_ylim([0, 100])
    if show_legend:
        ax.legend(loc='best', prop={'size':12})

    # get formatting
    plt.rcParams.update({'font.size': 14})
    plt.tight_layout()
    if save_to_disc:
        plt.savefig(output_path2)
    if show_in_screen:
        plt.show()
    plt.close(fig)
