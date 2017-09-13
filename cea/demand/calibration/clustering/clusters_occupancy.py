import pandas as pd
import os
from cea.demand.calibration.clustering.clustering_main import clustering_main, optimization_clustering_main
import cea.globalvar as gv
import cea.inputlocator as inputlocator
import seaborn
import matplotlib.pyplot as plt
from cea.analysis.mcda import mcda_cluster_main
from cea.utilities import dbfreader



# Local variables
gv = gv.GlobalVariables()
scenario_path = gv.scenario_reference
locator = inputlocator.InputLocator(scenario_path=scenario_path)
data_folder_path = r'C:\Users\Jimeno\Desktop\data'
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']

wanna_optimize = False # if False it gets the minimum number of clusters.
wanna_create_plots = False
wanna_create_2D_map_data =True

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

    if wanna_create_plots:
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

if wanna_create_2D_map_data:
    output_file1 = 'type_restaurant_Singapore_timeseriesdata.dbf'
    output_path1 = os.path.join(locator.get_calibration_clustering_plots_folder(), output_file1)
    for i, day in enumerate(days):
        data = pd.read_csv(os.path.join(data_folder_path, 'type_restaurant_Singapore_' + day + '.csv'))
        if i == 0:
            initial_date = pd.date_range('1/1/2010', periods=24, freq='H')
            time = initial_date.strftime("%Y%m%d%H%M%S")
        else:
            date = initial_date.shift(i, freq='D')
            time = date.strftime("%Y%m%d%H%M%S")
        columns = [str(x) for x in range(24)]
        data_matrix = data.as_matrix(columns=columns)

        for building in range(data.place_id.count()):
            series = pd.DataFrame(
                {'time': time, 'freq': data_matrix[building], 'long': data.loc[building, 'lng'],
                 'lat': data.loc[building, 'lat']})
            if i == 0 and building == 0:
                series_final = series
            else:
                series_final = series_final.append(series, ignore_index=True)

    dbfreader.dataframe_to_dbf(series_final, output_path1)

    #         index = 0
    #         for building_name, sensors_number_building, sensor_code_building in zip(names_zone, sensors_number_zone,
    #                                                                                 sensors_code_zone):
    #             selection_of_results = solar_res[index:index + sensors_number_building]
    #             items_sensor_name_and_result = dict(zip(sensor_code_building, selection_of_results))
    #             with open(locator.get_radiation_building(building_name), 'w') as outfile:
    #                 json.dump(items_sensor_name_and_result, outfile)
    #             index = sensors_number_building
    #
    # a = data_matrix.flatten()
    # if day == 'Monday':
    # date = pd.date_range('1/1/2010', periods=24*len(days), freq='H')
    # location = locator.get_solar_radiation_folder()
    # time = date.strftime("%Y%m%d%H%M%S")
    #
    # for i, building in enumerate(buildings):
    #     data = pd.read_csv(os.path.join(location, building + '_geometry.csv'))
    #     geometry = data.set_index('SURFACE')
    #     solar = pd.read_csv(os.path.join(location, building + '_insolation_Whm2.csv'))
    #     surfaces = solar.columns.values
    #
    #     for surface in surfaces:
    #         Xcoor = geometry.loc[surface, 'Xcoor']
    #         Ycoor = geometry.loc[surface, 'Ycoor']
    #         Zcoor = geometry.loc[surface, 'Zcoor']
    #         result = pd.DataFrame({'date': time, 'surface': building + surface,
    #                                'I_Wm2': solar[surface].values[period[0]: period[1]],
    #                                'Xcoor': Xcoor, 'Ycoor': Ycoor, 'Zcoor': Zcoor})
    #         if i == 0:
    #             final = result
    #         else:
    #             final = final.append(result, ignore_index=True)
    #
    # dbfreader.dataframe_to_dbf(final, locator.get_solar_radiation_folder() + "result_solar_48h.dbf")


