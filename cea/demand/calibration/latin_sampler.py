from __future__ import division
from scipy.stats import triang
from scipy.stats import norm
from scipy.stats import uniform
from sklearn import preprocessing

from cea.utilities import latin_hypercube
import pandas as pd

__author__ = "Jimeno A. Fonseca"
__copyright__ = "Copyright 2017, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"


def latin_sampler(locator, num_samples, variables):
    """
    This script creates a matrix of m x n samples using the latin hypercube sampler.
    for this, it uses the database of probability distribtutions stored in locator.get_uncertainty_db()
    it returns clean and normalized samples.

    :param locator: pointer to locator of files of CEA
    :param num_samples: number of samples to do
    :param variables: list of variables to sample
    :return:
        1. design: a matrix m x n with the samples where each feature is normalized from [0,1]
        2. design_norm: a matrix m x n with the samples where each feature is normalized from [0,1]
        2. pdf_list: a dataframe with properties of the probability density functions used in the excercise.
    """

    # get probability density function PDF of variables of interest
    variable_groups = ('ENVELOPE', 'INDOOR_COMFORT', 'INTERNAL_LOADS')
    database = pd.concat([pd.read_excel(locator.get_uncertainty_db(), group, axis=1)
                          for group in variable_groups])
    pdf_list = database[database['name'].isin(variables)].set_index('name')

    # get number of variables
    num_vars = pdf_list.shape[0]  # alternatively use len(variables)

    # get design of experiments
    samples = latin_hypercube.lhs(num_vars, samples=num_samples)
    samples_norm = samples.copy()
    for i, variable in enumerate(variables):
        # normalization of data:
        distribution = pdf_list.loc[variable, 'distribution']
        #sampling into lhs
        min = pdf_list.loc[variable, 'min']
        max = pdf_list.loc[variable, 'max']
        mu = pdf_list.loc[variable, 'mu']
        stdv = pdf_list.loc[variable, 'stdv']
        if distribution == 'triangular':
            loc = min
            scale = max - min
            c = (mu - min) / (max - min)
            samples[:, i] = triang(loc=loc, c=c, scale=scale).ppf(samples[:, i])
        elif distribution == 'normal':
            samples[:, i] = norm(loc=mu, scale=stdv).ppf(samples[:, i])
        else:  # assume it is uniform
            samples[:, i] = uniform(loc=min, scale=max).ppf(samples[:, i])

        #sampling into lhs normalized
        arguments = [min, max, mu,stdv]
        min_max_scaler = preprocessing.MinMaxScaler(copy=True, feature_range=(0, 1))
        arguments_norm = min_max_scaler.fit_transform(arguments)
        min = arguments_norm[0]
        max = arguments_norm[1]
        mu = arguments_norm[2]
        stdv = arguments_norm[3]
        if distribution == 'triangular':
            loc = min
            scale = max - min
            c = (mu - min) / (max - min)
            samples_norm[:, i] = triang(loc=loc, c=c, scale=scale).ppf(samples_norm[:, i])
        elif distribution == 'normal':
            samples_norm[:, i] = norm(loc=mu, scale=stdv).ppf(samples_norm[:, i])
        else:  # assume it is uniform
            samples_norm[:, i] = uniform(loc=min, scale=max).ppf(samples_norm[:, i])

    return [samples, samples_norm], pdf_list
