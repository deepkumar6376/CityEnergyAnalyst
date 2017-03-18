def test_graphs_optimization():
    import cea.globalvar
    import cea.inputlocator
    import numpy as np
    import pandas as pd
    import os
    import pickle
    from pickle import Unpickler, Pickler
    from deap import base
    from deap import creator
    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)
    generation = 1
    os.chdir(locator.get_optimization_master_results_folder())

    # pop = { "lion": "yellow", "kitty": "red" }
    # g = 1
    # ntwList = []
    # epsInd = { "lion": "yellow", "kitty": "red" }
    # invalid_ind = { "lion": "yellow", "kitty": "red" }
    # fitnesses = { "lion": "yellow", "kitty": "red" }
    #
    # with open("CheckPointTrial" + str(g), "wb") as CPwrite:
    #
    #     CPpickle = Pickler(CPwrite)
    #     cp = dict(population=pop, generation=g, networkList=ntwList, epsIndicator=epsInd, testedPop=invalid_ind,
    #               objective=fitnesses)
    #     CPpickle.dump(cp)

    with open("CheckPointTrial1", "rb") as CPread:
        CPunpick = Unpickler(CPread)
        cp = CPunpick.load()
        # cp = pickle.load(CPread)
        pop = cp["population"]
        ntwList = cp["networkList"]
        epsInd = cp["epsIndicator"]
        print (pop)



if __name__ == '__main__':
    test_graphs_optimization()
