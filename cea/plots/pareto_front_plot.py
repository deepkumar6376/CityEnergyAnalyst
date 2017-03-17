def test_graphs_optimization():
    import cea.globalvar
    import cea.inputlocator
    import pandas as pd
    import os
    from pickle import Unpickler
    from deap import base
    from deap import creator
    gv = cea.globalvar.GlobalVariables()
    scenario_path = gv.scenario_reference
    locator = cea.inputlocator.InputLocator(scenario_path)
    generation = 1
    genCP = generation
    os.chdir(locator.get_optimization_master_results_folder())

    with open("CheckPoint" + str(genCP), "rb") as CPread:
        CPunpick = Unpickler(CPread)
        cp = CPunpick.load()
        pop = cp["population"]
        eps = cp["epsIndicator"]
        testedPop = cp["testedPop"]


    data_container = [['Cost', 'CO2', 'Eprim_i']]
    ind_counter = 0
    for ind in pop:
        # FIXME: possibly refactor a: inline, also, this construction is weird...
        a = [ind.fitness.values]
        CO2 = [int(i[0]) for i in a]
        cost = [int(i[1]) for i in a]
        Eprim = [int(i[2]) for i in a]

        key = pop[ind_counter]


        features = [CO2[:], cost[:], Eprim[:]]
        data_container.append(features)
        ind_counter += 1
    results = pd.DataFrame(data_container)

    print (results)

if __name__ == '__main__':
    test_graphs_optimization()
