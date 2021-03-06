import os
import pandas as pd
import pyliburo.py3dmodel.calculate as calculate
from pyliburo import py3dmodel
import pyliburo.py2radiance as py2radiance
import json

import pyliburo.gml3dmodel as gml3dmodel
__author__ = "Jimeno A. Fonseca"
__copyright__ = "Copyright 2017, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Jimeno A. Fonseca", "Kian Wee Chen"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"


def create_sensor_input_file(rad, chunk_n):
    sensor_file_path = os.path.join(rad.data_folder_path, "points_"+str(chunk_n)+".pts")
    sensor_file = open(sensor_file_path, "w")
    sensor_pts_data = py2radiance.write_rad.sensor_file(rad.sensor_positions, rad.sensor_normals)
    sensor_file.write(sensor_pts_data)
    sensor_file.close()
    rad.sensor_file_path = sensor_file_path


def generate_sensor_surfaces(occface, xdim, ydim, srf_type):
    normal = py3dmodel.calculate.face_normal(occface)
    mid_pt = py3dmodel.calculate.face_midpt(occface)
    location_pt = py3dmodel.modify.move_pt(mid_pt, normal, 0.01)
    moved_oface = py3dmodel.fetch.shape2shapetype(py3dmodel.modify.move(mid_pt, location_pt, occface))
    # put it into occ and subdivide surfaces
    sensor_surfaces = py3dmodel.construct.grid_face(moved_oface, xdim, ydim)

    # calculate list of properties per surface
    sensor_dir = [normal for x in sensor_surfaces]
    sensor_cord = [py3dmodel.calculate.face_midpt(x) for x in sensor_surfaces]
    sensor_type = [srf_type for x in sensor_surfaces]
    sensor_area = [calculate.face_area(x)for x in sensor_surfaces]

    return sensor_dir, sensor_cord, sensor_type, sensor_area


def calc_sensors_building(building_geometry_dict, sensor_parameters):
    sensor_dir_list = []
    sensor_cord_list = []
    sensor_type_list = []
    sensor_area_list = []
    surfaces_types = ['walls', 'windows', 'roofs']
    for srf_type in surfaces_types:
        occface_list = building_geometry_dict[srf_type]
        for face in occface_list:
            sensor_dir, sensor_cord, sensor_type, sensor_area \
                = generate_sensor_surfaces(face, sensor_parameters['X_DIM'], sensor_parameters['Y_DIM'], srf_type)

            sensor_dir_list.extend(sensor_dir)
            sensor_cord_list.extend(sensor_cord)
            sensor_type_list.extend(sensor_type)
            sensor_area_list.extend(sensor_area)

    return sensor_dir_list, sensor_cord_list, sensor_type_list, sensor_area_list


def calc_sensors_zone(geometry_3D_zone, locator, sensor_parameters):
    sensors_coords_zone = []
    sensors_dir_zone = []
    sensors_total_number_list = []
    names_zone = []
    sensors_code_zone = []
    for building_geometry in geometry_3D_zone:
        # building name
        bldg_name = building_geometry["name"]
        # get sensors in the building
        sensors_dir_building, sensors_coords_building, \
        sensors_type_building, sensors_area_building = calc_sensors_building(building_geometry, sensor_parameters)

        # get the total number of sensors and store in lst
        sensors_number = len(sensors_coords_building)
        sensors_total_number_list.append(sensors_number)

        sensors_code = ['srf' + str(x) for x in range(sensors_number)]
        sensors_code_zone.append(sensors_code)

        # get the total list of coordinates and directions to send to daysim
        sensors_coords_zone.extend(sensors_coords_building)
        sensors_dir_zone.extend(sensors_dir_building)

        # get the name of all buildings
        names_zone.append(bldg_name)

        # save sensors geometry result to disk
        pd.DataFrame({'BUILDING':bldg_name,
                      'SURFACE': sensors_code,
                      'Xcoor': [x[0] for x in sensors_coords_building],
                      'Ycoor': [x[1] for x in sensors_coords_building],
                      'Zcoor': [x[2] for x in sensors_coords_building],
                      'Xdir': [x[0] for x in sensors_dir_building],
                      'Ydir':[x[1] for x in sensors_dir_building],
                      'Zdir':[x[2] for x in sensors_dir_building],
                      'AREA_m2': sensors_area_building,
                      'TYPE': sensors_type_building}).to_csv(locator.get_radiation_metadata(bldg_name), index=None)


    return sensors_coords_zone, sensors_dir_zone, sensors_total_number_list, names_zone, sensors_code_zone


def isolation_daysim(chunk_n, rad, geometry_3D_zone, locator, weather_path, settings):

    # folder for data work
    daysim_dir = locator.get_temporary_file("temp" + str(chunk_n))
    rad.initialise_daysim(daysim_dir)

    # calculate sensors
    print " calculating and sending sensor points"
    sensors_coords_zone, sensors_dir_zone, sensors_number_zone, names_zone, \
    sensors_code_zone = calc_sensors_zone(geometry_3D_zone, locator, settings.sensor_parameters)
    rad.set_sensor_points(sensors_coords_zone, sensors_dir_zone)
    create_sensor_input_file(rad, chunk_n)

    num_sensors = sum(sensors_number_zone)
    print "Daysim simulation starts for building(s)", names_zone
    print "and the next number of total sensors", num_sensors
    if num_sensors > 10000:
        raise ValueError('You are sending more than 10000 sensors at the same time, this \
                          will eventually crash a daysim instance. To solve it, reduce the number of buildings \
                          in each chunk in the Settings.py file')

    rad.execute_epw2wea(weather_path)
    rad.execute_radfiles2daysim()
    rad_params = settings.rad_parameters
    rad.write_radiance_parameters(rad_params['RAD_AB'], rad_params['RAD_AD'], rad_params['RAD_AS'],
                                  rad_params['RAD_AR'], rad_params['RAD_AA'], rad_params['RAD_LR'],
                                  rad_params['RAD_ST'], rad_params['RAD_SJ'], rad_params['RAD_LW'],
                                  rad_params['RAD_DJ'], rad_params['RAD_DS'], rad_params['RAD_DR'],
                                  rad_params['RAD_DP'])
    rad.execute_gen_dc("w/m2")
    rad.execute_ds_illum()
    solar_res = rad.eval_ill_per_sensor()

    print "Writing results to disk"
    index = 0
    for building_name, sensors_number_building, sensor_code_building in zip(names_zone, sensors_number_zone, sensors_code_zone):
        selection_of_results = solar_res[index:index+sensors_number_building]
        items_sensor_name_and_result = dict(zip(sensor_code_building, selection_of_results))
        with open(locator.get_radiation_building(building_name), 'w') as outfile:
            json.dump(items_sensor_name_and_result, outfile)
        index = sensors_number_building