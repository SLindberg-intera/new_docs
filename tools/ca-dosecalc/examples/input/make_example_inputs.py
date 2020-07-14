copcs = ['C14','Cl36','H3','I129','Np237','Ra226','Re187','Sr90','Tc99','Th230','U232','U233','U234','U235','U236','U238']

soils = [0,1,2,3,4,5,6]
pathways = ['External Gamma','Inhalation','Inhalation Vapor','Soil','Drinking Water','Produce','Beef','Milk','Poultry','Egg','Fish','Total']

def gen_dose_factors():
    for copc in copcs:
        for soil in soils:
            for pathway in pathways:
                yield ",".join(map(str, [soil, 1, pathway, copc, 1, 1]))

with open('tempdose.csv', 'w') as f:
    f.write("\n".join(list(gen_dose_factors())))

def gen_copc():
    for copc in copcs:
        yield ",".join(map(str, [1, copc, copc, copc, -1, 3, 1e-6, 'rad']))

with open('tempcopc.csv', 'w') as f:
    f.write("\n".join(list(gen_copc())))

def gen_pathways():
    for pathway in pathways:
        yield ",".join(map(str, [1, pathway, pathway]))

with open('pathways.csv', 'w') as f:
    f.write("\n".join(list(gen_pathways())))
