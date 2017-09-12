import pandas as pd
import os
from cea.demand.calibration.clustering.clustering_main import clustering_main


data_folder_path = r'C:\Users\Jimeno\Desktop\data'
locator =

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
for day in days:
    data = pd.read_csv(os.path.join(data_folder_path, 'type_restaurant_Singapore_' + day + '.csv'))
    columns = [str(x) for x in range(24)]
    data_matrix = data.as_matrix(columns=columns)

    # calculate sax for timesieries data
    word_size = 4
    alphabet_size = 3
    clustering_main(locator=locator, data=data, word_size=word_size, alphabet_size=alphabet_size)



    #plot
    show_benchmark = True
    save_to_disc = True
    show_in_screen = False
    show_legend = False
    labelx = "Hour of the day"
    labely = "Electrical load [kW]"
    # input_path = demand_CEA_reader(locator=locator, building_name=name, building_load=building_load,
    #                  type=type_data)
    #
    # input_path = pd.DataFrame(dict((str(key), value) for (key, value) in enumerate(input_path)))

    input_path = locator.get_calibration_cluster('clusters_mean')
    output_path = os.path.join(locator.get_calibration_clustering_plots_folder(),
                               "w_a_" + str(word_size) + "_" + str(alphabet_size) + "_building_name_" + name + ".png")

    clusters_day_mean(input_path=input_path, output_path=output_path, labelx=labelx,
                      labely=labely, save_to_disc=save_to_disc, show_in_screen=show_in_screen,
                      show_legend=show_legend)  # , show_benchmark=show_benchmark)
