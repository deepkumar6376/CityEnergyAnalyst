import pandas as pd
import os
from cea.demand.calibration.clustering.clustering_main import clustering_main, clusters_day_mean
import cea.globalvar as gv
import cea.inputlocator as inputlocator
import seaborn
import matplotlib.pyplot as plt

data_folder_path = r'C:\Users\Jimeno\Desktop\data'

gv = gv.GlobalVariables()
scenario_path = gv.scenario_reference
locator = inputlocator.InputLocator(scenario_path=scenario_path)

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
for day in days:
    output_file1= 'type_restaurant_Singapore_' + day + 'box_plot.png'
    output_file2 = 'type_restaurant_Singapore_' + day + 'cluster.png'
    output_path1 = os.path.join(locator.get_calibration_clustering_plots_folder(), output_file1)
    output_path2 = os.path.join(locator.get_calibration_clustering_plots_folder(), output_file2)
    data = pd.read_csv(os.path.join(data_folder_path, 'type_restaurant_Singapore_' + day + '.csv'))
    columns = [str(x) for x in range(24)]
    data_matrix = data.as_matrix(columns=columns)

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
    word_size = 3
    alphabet_size = 4
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
