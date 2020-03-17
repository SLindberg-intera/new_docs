"""
    build_surface_flux.py
	version 1.1:  Fixed issues with grid axis having multiple lines
				  in the get_variables function, Neil Powers, 20190610
-----------------------
Description:
    1) read STOMP input file, extract grid card
    2) read modflow shapefile, extract grids using stomp grid coordinates
    3) Create ~surface flux card mapping the stomp grid into the modflow grids
    4) Validation:
        a) validate stomp grid
        b) validate none of the nodes in the stomp grid stradle 2 grids in modflow
           shapefile
    5) output:
        a) text file with stomp ~surface flux card
        b) CSV file showing which nodes fit within which shapefile _grid_conversion
        c) log file

Developed by:
    Eugene O Powers
Company:
    INTERA, INC

written for python 3.5
  - assumes pyshp
  -   if you don't have these libraries, try the following:
           python -m pip install pyshp
  - funded by
     a) CHPRC.C003.HANOFF Rel 61
History
    Version 1.0.0 11-Apr-2018:
        Initial version
    Version 1.0.1 23-May-2018:
        Changed ci/year to 1/year

"""
import shapefile
import datetime
import os
import argparse
import logging
from operator import itemgetter

comment =  '#--  Surface Flux Card Auto generated using Python scrip:\n'
comment += '#--       build_surface_flux.py\n'
comment += '#--  Script written by:\n'
comment += '#--       Eugene O Powers\n'
comment += '#--       Intera, Inc.\n'
comment += '#--  Script version:\n'
comment += '#--       1.0\n'
#-------------------------------------------------------------------------------
# validate contaminates
# 22 Nov 2019, EOP, removed as obsolete do to requirement changed
#def validate_contaminates(contaminates):
#    legal_names = ['U-232','U-233','U-234','U-235','U-236','U-238',
#                          'Th-230','Ra-226','C-14','Cl-36','H-3','I-129',
#                          'Np-237','Re-187','Sr-90','Tc-99']
#    bad_names = []
#    for name in contaminates:
#        if name not in legal_names:
#            bad_names.append(name)
#    if len(bad_names) > 0:
#        logger.info('ERROR: Invalid contaminate names:  {0}'.format(bad_names))
#        return False
#    return True


#-------------------------------------------------------------------------------
# set up Log handler
def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    # set a format which is simpler for console use

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
#-------------------------------------------------------------------------------
# read ~grid card from file
def get_variables(filename):
    #logging.debug('START get_variables: %s',filename)
    var = []
    grid_card = 'false'
    i = 0
    with open(filename) as data:
    #    logging.debug('get_variables=>opened file: %s',filename)
        grid = []
        x = -1
        check = False
        for line in data:
            if grid_card == 'true':
                l = line.rstrip()
                l = l.rstrip(',')

                if check:
                    temp = l[0:-1].split(',')
                    if '@' in temp[0]:
                        grid[x-1].extend(temp)
                    else:
                        check = False
                        #x += 1
                if not check:
                    x += 1
                    if x == 1:
                        grid.append(l[0:-1].split(','))
                    if x == 2:
                        grid.append(l.split(','))
                    if x == 3:
                        grid.append(l[0:-1].split(','))
                        check = True
                    if x == 4:
                        grid.append(l[0:-1].split(','))
                        check = True
                    if x == 5:
                        grid.append(l[0:-1].split(','))
                        check = True
                    if x == 6:
                        print(grid)
                        return grid
            elif line.find('~Grid Card',0) == 0:
    #            logging.debug('get_variables=>card Found: %s',line[:line.find('\r\n')])
                grid_card = 'true'
    return grid
#-------------------------------------------------------------------------------
# build stomp indexes
def build_ind(text,num):
    ind = [None] *( num +1)
    i = 0
    for x in text:
        ####
        # if index is larger than num then the grid is wrong
        if i > num and len(x) != 0:
            return ['ERROR: Index should have {0} values, has {1} found.'.format(num,i)]

        if is_number(x):
            ind[0] = float(x)
            i += 1
        elif '@' in x:
            temp = x.split('@')
            count = int(temp[0])
            exp = float(temp[1])
            for z in range (0, count):
                ind[i] = ind[i-1] + exp
                i += 1
    ####
    # if the index is smaller than num then the grid is wrong
    if (i-1) != num:
        return ['ERROR: Index should have {0} values, only {1} found.'.format(num,i)]
    return ind
#-------------------------------------------------------------------------------
# find if a string can be converted to float
def is_number(s):
    try:
        float(s)
        return True
    except:
        return False
#-------------------------------------------------------------------------------
# read in shape file then find all relevant grids to the stomp grid
def build_shp_grid(shpfile,ind_x,ind_y,num_x,num_y):
    sf = shapefile.Reader(shpfile)
    shapes = sf.shapes()
    shapeRecs = sf.shapeRecords()
    fields = sf.fields[1:]
    logging.info([field[0] for field in fields])
    i = 0
    nodes = []
    x_start = float(ind_x[0])
    x_end = float(ind_x[num_x])
    y_start = float(ind_y[0])
    y_end = float(ind_y[num_y])
    for shaperec in shapeRecs:
        shape =shapes[i]
        i+=1
        bbox = shape.bbox
        if x_start <= float(bbox[0]) <= x_end:
            if y_start <= float(bbox[1]) <= y_end:
                if float(bbox[0]) != x_end and float(bbox[1]) != y_end:

                    nodes.append({'x':float(bbox[0]), 'y':float(bbox[1]),'x_end':float(bbox[2]),'y_end':float(bbox[3]),
                              'node':shaperec.record[5],'row':shaperec.record[0],'column':shaperec.record[1],'delx':shaperec.record[2],'dely':shaperec.record[3]})
    if len(nodes) < 1:
        logging.critical('ERROR: could not find grids between(x:{0},y:{1} and x:{2},y:{3}): {0}'.format(x_start,y_start,x_end, y_end))
        raise
    return sorted(nodes, key=itemgetter('y','x'))
#-------------------------------------------------------------------------------
# output ~solute flux card and csv of Stomp file grid to shape file grid
# conversion
def write_outputs(template):
    o = ''
    with open(template, "r") as t:

        #logger.info('Successfully opened template:  {0}'.format(template))
        o = t.read()
        repeat = True
    try:
        while repeat:
            values = (yield)
            os.makedirs(os.path.dirname(values['csv_outfile'] ), exist_ok=True)
            filename = str(values['csv_outfile']).rstrip()# + 'input.txt'
            logging.info('writing csv grid conversion: {0}'.format(filename))
            with open(filename, "w") as out:
                out.write(values['csv'])
            #output = o.format(**values)
            os.makedirs(os.path.dirname(values['outfile'] ), exist_ok=True)
            filename = values['outfile'].rstrip()# + 'input.txt'
            logging.info('writing file: {0}'.format(filename))
            with open(str(filename), "w") as out:
                out.write(values['surface_flux'])



    except GeneratorExit:
        None
        logging.info('Finished building input files')
#-------------------------------------------------------------------------------
# main function
#-------------------------------------------------------------------------------
def main():
    ####
    # Setup Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--sim",help="Name of Sim Model", type=str, default="Unknown")
    parser.add_argument("-i","--inputfile", type=str, help="If an input file the file ~grid card from the file will be used other wise grid data will default to the sim template")
    parser.add_argument("-shp","--shapefile", type=str, help="shapefile to be used")
    parser.add_argument("-c","--con", nargs='+', type=str, help="Constituents used in this model")
    #parser.add_argument("-v","--valcontam",  action='store_false', help="Use this to bypass validation of the list of contaminate names")
    parser.add_argument("-o","--outfile", type=str, help="Directory and name of output file default: output/{model}/{date}/_solute_flux_card.txt")
    parser.add_argument("-csv","--csvfile", type=str, help="location to create csv file to check shapefile grid to stomp grid conversion. default: csv/{model}/{date}/{model}_grid_conversion.csv")
    parser.add_argument("-b","--boundaries",type=str, help="turn on boundaries for solute flux and Aqueous Volumetric. exampe: BNS will turn on bottom, North, and South. example 2(default): B will turn on bottom only. ", default="B")
    args = parser.parse_args()

    if not os.path.isdir('log'):
        os.mkdir('log')
    log = "error_modify_cards_log_"+cur_date.strftime("%Y%m%d")+".txt"

    lvl = logging.INFO
    logger = setup_logger('logger', 'log/'+log, lvl)
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(lvl)
    # tell the handler to use specified format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('logger').addHandler(console)

    text_dic = {}
    contaminates = []
    sim = 0;

    try:
        ####
        # process input arguments
        ####
        # Sim
        logger.info(args.inputfile)
        if args.sim:
            text_dic['model'] = args.sim.rstrip()

        if args.inputfile:
            template = args.inputfile.rstrip()



        #Constituents
        if args.con == None:
            logger.critical('Invalid inputs: Constituents not found')
            return ValueError('Invalid inputs')
        else:
            contaminates = args.con
        #outfile
        if args.outfile:
            text_dic['outfile'] = args.outfile.rstrip()
        else:
            text_dic['outfile'] = 'output/{0}/{1}/{0}_solute_flux_card.txt'.format(text_dic['model'],cur_date.strftime("%Y%m%d"))
        #csv
        if args.csvfile:
            text_dic['csv_outfile'] = args.csvfile.rstrip()
        else:
            text_dic['csv_outfile'] = 'csv/{0}/{1}/{0}_grid_conversion.csv'.format(text_dic['model'],cur_date.strftime("%Y%m%d"))
        #shpfile input
        if args.shapefile:
            shpfile = args.shapefile.rstrip()
        else:
            shpfile = "grid_attempt1/grid_attempt1"

        #start logging
        logger.info('*******************************************************')
        logger.info('** build stomp input file for {0}'.format(text_dic['model']))
        logger.info('*******************************************************')
        #####
        # validate inputs

        if not os.path.isfile(template):
            if not os.path.isfile(template):
                logger.critical('Invalid inputs: {0} '.format(template))
                logger.critical('                File not found, exiting script.')
                return ValueError('Invalid file')
        elif not os.path.isfile(shpfile):
            if not os.path.isfile(shpfile):
                logger.critical('Invalid inputs: {0} '.format(shpfile))
                logger.critical('                File not found, exiting script.')
                return ValueError('Invalid file')
#        22 Nov 2019 removed due to requirement change
#        if args.valcontam:
#            if not validate_contaminates(contaminates):
#                logger.critical('                invalid contaminates, exiting script.')
#                return ValueError('Invalid contaminate list')
        text_dic['date'] = cur_date.strftime("%m/%d/%Y")
        text_dic['time'] = time.strftime("%I:%M %p UTC")


        #------------------------------------------------------------------
        #~Grid Card
        grid = get_variables(template)
        num_x = int(grid[1][0])
        num_y = int(grid[1][1])
        num_z = int(grid[1][2])
        #******
        #** build x index values
        ind_x = build_ind(grid[2],num_x)
        if len(ind_x) <= 1:
            logger.critical('Build i Index failed with below error:')
            logger.critical(ind_x[0])
            logger.critical('       Invalid Stomp Grid, exiting script.')
            return ValueError('Invalid file')
        #******
        #** build x index values
        ind_y = build_ind(grid[3],num_y)
        if len(ind_y) <= 1:
            logger.critical('Build j Index failed with below error:')
            logger.critical(ind_y[0])
            logger.critical('       Invalid Stomp Grid, exiting script.')
            return ValueError('Invalid file')
        #******
        #** log input data
        logger.info('input data:')
        logger.info('       stomp grid file: {0}'.format(template))
        logger.info('            Shape file: {0}'.format(shpfile))
        logger.info('          Constituents: {0}'.format(contaminates))
        logger.info('      solute flux file: {0}'.format(text_dic['outfile']))
        logger.info('  grid conversion file: {0}'.format(text_dic['csv_outfile']))
        logger.info('       stomp grid size: {0},{1},{2}'.format(num_x, num_y, num_z))
        logger.info('          stomp grid x: {0}'.format(grid[2]))
        logger.info('          stomp grid i: {0}'.format(ind_x))
        logger.info('          stomp grid y: {0}'.format(grid[3]))
        logger.info('          stomp grid j: {0}'.format(ind_y))
        logger.info('          stomp grid k: {0}'.format(grid[4]))
        #******
        #** Find all shapefile nodes that fall in x - y boundaries
        nodes = build_shp_grid(shpfile,ind_x,ind_y,num_x,num_y)
        logger.info('      shape_file_grids: ')
        for node in nodes:
            logger.info('                         {0}'.format(node))
        logger.info('building solute flux card')

        tmp = ''
        #******
        #** solute flux card text
        filename = '{0}, srf/modflow_{1}-{2}.srf,\n'
        filename2 = '{1}, srf/{0}.srf,\n'
        comment = '#Bottom Flux for P2R Surface {0},{1}\n'
        line = 'Solute Flux, {0}, 1/yr, , Bottom, {1}, {2}, {3}, {4}, 1, 1,\n'
        line_av = 'Aqueous Volumetric, m^3/yr, m^3, Bottom, {1}, {2}, {3}, {4}, 1, 1,\n'
        bottom = 'Solute Flux,{0}, 1/yr,, Bottom, 1, {1}, 1, {2}, 1, 1,\n'
        south = 'Solute Flux,{0}, 1/yr,, South, 1, {1}, 1, 1, 1, {2},\n'
        north = 'Solute Flux,{0}, 1/yr,, North, 1, {1}, {2}, {2}, 1, {3},\n'
        west = 'Solute Flux,{0}, 1/yr,, West, 1, 1, 1, {1}, 1, {2},\n'
        east = 'Solute Flux,{0}, 1/yr,, East, {1}, {1}, 1, {2}, 1, {3},\n'
        tmp2 = ''
        #tmp += filename2.format('water-mass-balance')
        #tmp += temp2
        count = 0
        temp_count = 0
        if "B" in args.boundaries.upper():
            tmp2 += 'Aqueous Volumetric, m^3/yr, m^3, Bottom, 1, {0}, 1, {1}, 1, 1,\n'.format(num_x,num_y)
            temp_count +=1
        if "S" in args.boundaries.upper():
            tmp2 += 'Aqueous Volumetric, m^3/yr, m^3, South, 1, {0}, 1, 1, 1, {1},\n'.format(num_x,num_z)
            temp_count +=1
        if "N" in args.boundaries.upper():
            tmp2 += 'Aqueous Volumetric, m^3/yr, m^3, North, 1, {0}, {1}, {1}, 1, {2},\n'.format(num_x,num_y,num_z)
            temp_count +=1
        if "W" in args.boundaries.upper():
            tmp2 += 'Aqueous Volumetric, m^3/yr, m^3, West, 1, 1, 1, {0}, 1, {1},\n'.format(num_y,num_z)
            temp_count +=1
        if "E" in args.boundaries.upper():
            tmp2 += 'Aqueous Volumetric, m^3/yr, m^3, East, {0}, {0}, 1, {1}, 1, {2},\n'.format(num_x,num_y,num_z)
            temp_count +=1
        tmp += filename2.format('water-mass-balance', temp_count)
        tmp += tmp2
        count += temp_count;
        for con in contaminates:
            tmp2 = ''
            temp_count = 0
            if "B" in args.boundaries.upper():
                tmp2 += bottom.format(con,num_x,num_y)
                temp_count +=1
            if "S" in args.boundaries.upper():
                tmp2 += south.format(con,num_x,num_z)
                temp_count +=1
            if "N" in args.boundaries.upper():
                tmp2 += north.format(con,num_x,num_y,num_z)
                temp_count +=1
            if "W" in args.boundaries.upper():
                tmp2 += west.format(con,num_y,num_z)
                temp_count +=1
            if "E" in args.boundaries.upper():
                tmp2 += east.format(con,num_x,num_y,num_z)
                temp_count +=1
            tmp += filename2.format(con+'-mass-balance', temp_count)
            tmp += tmp2
            count += temp_count
        #******
        #** find all of the y indexes that fall in each shapefile grid

        text_dic['csv'] = 'p2r,p2r,p2r,p2r,p2r,p2r,STOMP grid,STOMP grid,STOMP grid,STOMP grid,\nI,J,x_start,x_end,y_start,y_end,i_start,i_end,j_start,j_end,\n'
        for rec in nodes:
            x = 1
            x_start = 0
            x_end = 1
            #******
            #** find all of the x indexes that fall in each shapefile grid
            for x_ind in ind_x:
                if rec['x'] <= float(x_ind) < rec['x_end']:
                    #logger.info('node{0}: x({1}) <= j-{4}({2}) < x_end({3})'.format(rec['node'],rec['x'],x_ind,rec['x_end'],x))
                    if rec['x'] == float(x_ind) :
                        x_start = x
                    if x_end < x:
                        x_end = x

                x += 1
            if ind_x[x_end] != rec['x_end']:
                logger.critical('ERROR:  index i ({0}) stradles 2 grids'.format(x_end))
                logger.critical('          Stomp Grid range of i: {0} - {1}'.format(ind_x[x_end-1],ind_x[x_end]))
                logger.critical('        shpfile grid range of x: {0} - {1}'.format(rec['x'],rec['x_end']))
                logger.critical('        Invalid Stomp Grid, Exiting script.')
                return ValueError('Invalid Stomp Grid')
            y = 1
            y_start = 0
            y_end = 1
            #******
            #** find all of the y indexes that fall in each shapefile grid
            for y_ind in ind_y:
                if rec['y'] <= float(y_ind) < rec['y_end']:
                    #logger.info('node{0}: y({1}) <= j-{4}({2}) < y_end({3})'.format(rec['node'],rec['y'],y_ind,rec['y_end'],y))
                    if 0 == y_start :
                        y_start = y
                    if y_end < y:
                        y_end = y
                y += 1
            text_dic['csv'] += '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},\n'.format(rec['column'],rec['row'],rec['x'],rec['x_end'],rec['y'],rec['y_end'],
                                                                                        x_start, x_end, y_start,y_end)
            tmp += filename.format(len(contaminates)+1,rec['row'],rec['column'])
            tmp += comment.format(rec['row'],rec['column'])
            tmp += line_av.format('Aqueous Volumetric',x_start,x_end,y_start,y_end)
            count +=1
            for contaminate in contaminates:
                tmp += line.format(contaminate,x_start,x_end,y_start,y_end)
                count+=1
        #**********
        # build comments for surface flux card
        text_dic['surface_flux'] = '#------------------------------------------------------------------\n'
        text_dic['surface_flux'] += '~Surface Flux Card\n'
        text_dic['surface_flux'] += '#---------------------------------------------------------\n'
        text_dic['surface_flux'] += '{0},\n#Mass Balance Information\n{1}'.format(count,tmp)
        wo = write_outputs(template)
        wo.__next__()
        wo.send(text_dic)
        wo.close()
    except Exception as e:
        logger.critical('Unexpected Error: %s',e,exc_info=True)



#-------------------------------------------------------------------------------
# Start main process
if __name__ == "__main__":
    #-------------------------------------------------------------------------------
    # build globals
    cur_date  = datetime.date.today()
    time = datetime.datetime.utcnow()
    formatter = logging.Formatter('%(asctime)-9s: %(levelname)-8s: %(message)s','%H:%M:%S')
    #logger.info('\n{0}'.format(comment))
    testout = main()
