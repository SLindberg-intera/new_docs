copcs = ['C14','Cl36','H3','I129','Np237','Ra226','Re187','Sr90','Tc99','Th230','U232','U233','U234','U235','U236','U238']

soils = [0,1,2,3,4,5,6]
soilnames = ['none', 'Rupert Sand', 'Koehler Sand', 'Dune Sand', 'Burbank Loamy Sand', 'Ephrate Sandy Loam', 'Kiona Silt Loam']
pathways = ['External Gamma','Inhalation','Inhalation Vapor','Soil','Drinking Water','Produce','Beef','Milk','Poultry','Egg','Total without Fish']

doseFactor = 0.5
def gen_dose_factors():
    header = ['SOIL_INDEX','SOIL_CATEGORY','COPC','Pathway','Dose Factor']
    yield ",".join(header)
    for copc in copcs:
        for soilindex in soils:
            for pathway in pathways:
                soil = soilnames[soilindex]
                out = [soilindex, soil, copc, pathway, doseFactor]
                yield ",".join(map(str, out))

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
