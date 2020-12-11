"""

This tool depends on two other modules:

  pylib\fingerprint
  pylib\backbone

"""
import sys, os
import json
import argparse
from constants import ICF_HOME
import matplotlib.pyplot as plt
import networkx as nx
from networkx.readwrite import json_graph
import sys, os
import argparse
import json
#from show_children import summarize_version as svc
#from show_ancestors import summarize_version as sva


try:
    from backbone import backbone

except (ImportError, ModuleNotFoundError):
    reporoot = os.path.abspath(
        os.path.join(os.path.abspath(__file__), '..','..'))
    if reporoot not in sys.path:
        sys.path.append(reporoot)
    from backbone import backbone

#------------------------------
#node builds data around product and version
# p = Product name
# v = version of product
class node:
    def __init__(self, p, v):
        self.product_name = p
        self.product_version = v
        #initialize private attributes
        self._product_status = None
        self._work_product = None
        self._product_path = None
        self._blockchain_filepath = None
        self._checkindate = None
        self._parents = None
        self._blockchain_dict = None
        self._children = None
        #self.product_arr.append(self.start_product)
        
    #------------------------------------------------
    #- start product controls
    @property
    def work_product(self):
        #format the full work product with version and status
        self._work_product = self.__format_work_product(self.product_name,self.product_version,self.product_status)
        return self._work_product
    @property
    def product_status(self):
        #get preduct status using the product_name and version
        if self._product_status is None:
            path = self.__get_product_path(self.product_name,self.product_version)
            _,_,self._product_status = self.__get_product_version_status(path)
        return self._product_status
    @property
    def product_path(self):
        #get product path using product name and version
        if self._product_path is None:
            self._product_path = self.__get_product_path(self.product_name, self.product_version)
        return self._product_path
    @property
    def blockchain_filepath(self):
        #get path to blockchain file for this product/version
        if self._blockchain_filepath is None:
            self._blockchain_filepath = self.__get_blockchain_file(self.product_path)
        return self._blockchain_filepath
    @property
    def parents(self):
        #get direct parents of the product/version
        if self._parents is None:
            self._parents = self.__get_direct_parents()
        return self._parents
    @property
    def children(self):
        #get direct children of the product/version
        if self._children is None:
            self._children = self.__get_direct_children()
        return self._children
    @property
    def checkindate(self):
        #get the checkindate from the blockchain file
        if self._checkindate is None:
            self._checkindate = self.blockchain_dict["Timestamp"]
        return self._checkindate 
    @property
    def blockchain_dict(self):
        #load the blockchain file into a dictionary
        if self._blockchain_dict is None:
            with open(self.blockchain_filepath, 'r') as f:
                self._blockchain_dict = json.load(f)
        return self._blockchain_dict

    #------------------------------------------------
    #- format the product name as product, version, status
    def __format_work_product(self, product,version,status):
        return "{}, {}, {}".format(product,version,status)

    #------------------------------------------------
    #- get blockchain file using product and version
    def __get_blockchain_file(self,base_path):
        filepath = os.path.join(base_path,"meta","icfblock.block")
        if os.path.exists(filepath):
            return filepath
        else:
            raise ValueError("Could not find blockchain file: {}".format(filepath))

    #------------------------------------------------
    #- build path to highest status of (IE Prod/Test) product.
    def __get_product_path(self, product, version):
        path = os.path.join(ICF_HOME, product, version)
        if os.path.exists(path.replace(backbone.ICF_TEST_DIR, backbone.ICF_PROD_DIR )):
            path = path.replace(backbone.ICF_TEST_DIR, backbone.ICF_PROD_DIR )
        elif not os.path.exists(path):
            raise ValueError("Invalid product and/or version: {}, {}".format(product,version))
        return path

    #------------------------------------------------
    #- strip product, version, status from path
    def __get_product_version_status(self,path):
        newpath, version = os.path.split(path)
        newpath, product = os.path.split(newpath)
        newpath, status = os.path.split(newpath)
        return product,version,status

    #------------------------------------------------
    #- strip blockchain file path, meta folder, product, 
    #- version, and status from path
    def __get_product_data_from_path(self, path):
        newpath = path
        valid_status=['test','prod']
        #check if this is the path to product/version, or if it
        # is a path to the blockchain file
        if backbone.ICF_BLOCK_FILENAME in path:
            newpath, blockfile = os.path.split(os.path.abspath(newpath))
            newpath, metadir = os.path.split(newpath)
        product, version, status = self.__get_product_version_status(newpath)
        '''
         paths taken from the blockchain files are currently based 
         on child path.  which means the directory is based off the 
         status of the child.
         example: (IE childpath/../../ancestor/ver/meta/icfblock.block)
         so if the status is not valid then you need to rebuild the 
         path using the product/version.
        '''
        if status.lower() not in valid_status:
            newpath = self.__get_product_path(product,version)
            product, version, status = self.__get_product_version_status(newpath)
            if status.lower() not in valid_status:
                raise ValueError("Could not find valid status for product: {}, {}".format(product,version))
        return product, version, status
    
    #------------------------------------------------
    #- get direct parent(s) of a product version
    def __get_direct_parents(self):
        arr_products = []

        #work_product = work_product +"," + checkedin
        for newPath in self.blockchain_dict["Inheritance"]:
            p, v, s = self.__get_product_data_from_path(newPath)
            f_product = self.__format_work_product(p,v,s)
            arr_products.append(f_product)
        
        return arr_products
    #------------------------------------------------
    #- get direct children of a product version
    def __get_direct_children(self):
        arr_products = []
        bb = backbone.WorkProductVersion(self.product_path)

        #get all product paths
        all_products_path = bb.all_work_products_path
        work_products = backbone.WorkProducts(all_products_path)

        #get all versions of each product
        product_version_paths = [[i.path for i in work_product.versions
                                    if (self.product_path not in i.path)]
                                        for work_product in work_products]

        #process each versions blockchain        
        for paths in product_version_paths:
            for path in paths:
                
                filepath = os.path.join(ICF_HOME, path, "meta","icfblock.block")
                if os.path.exists(filepath):
                    product, version, status = self.__get_product_data_from_path(filepath)
                    with open(filepath, 'r') as f:
                        d = json.load(f)
                        parents = d["Inheritance"]
                        
                        for newPath in parents:
                            #get product and version from path
                            t_product, t_version, _ = self.__get_product_data_from_path(newPath)
                            #check to see if it is equal to the parent version
                            if self.product_name == t_product and self.product_version == t_version:
                                
                                if not(product == self.product_name and version == self.product_version):
                                    arr_products.append(self.__format_work_product(product, version, status))
                else:
                    print('could not find path: {}'.format(filepath))
        return arr_products
#---------------------end class blockchain--------------------------

#-------------------------------------------------------------------
# Nodes
# builds network of node classes
#   p = name of product to start from
#   v = product version to start from
# --
#   network:  all products that can be traced to any related product/version (both children and ancestors)
#   ancestors: all ancestors of starting product
#   children: all children of starting product
class nodes:
    def __init__(self, p, v):
        self.starting_node = node(p,v)
        #self.getchildren=gc
        #self.getancestors=ga
        #initialize private attributes 
        self._network = None
        self._ancestors = None
        self._children = None
    @property
    def network(self):
        if self._network == None:
            self._network = self.__build_network()
        return self._network
    @property
    def ancestors(self):
        if self._ancestors == None:
            self._ancestors = self.__build_network('back')
        return self._ancestors
    @property
    def children(self):
        if self._children == None:
            self._children = self.__build_network('for')
        return self._children
    #--------------------------------------------------------
    #-
    def __add_to_array(self,arr,new_vals):
        for x in new_vals:
            if x not in arr:
                arr.append(x)
        return arr
    #--------------------------------------------------------
    #- build dictionary of all ancestors and children of each
    #- product {ancestor:blockchain}
    #- process (string): determine direction of build go through ancestors or children
    #-                      Valid values: back,for,all
    
    def __build_network(self, process='all'):
        def add_related(cur_node):
            if process.lower()=='all':
                new_arr = cur_node.parents
                return self.__add_to_array(new_arr,cur_node.children)
            elif process.lower()=='back':
                return cur_node.parents
            elif process.lower()=='for':
                return cur_node.children
            else:
                raise ValueError("Invalid value passed to build_network: {}".format(process))
        network = {}
        #checkindates = {}
        product_arr = []
        completed_arr = []
        #add starting node to values
        network[self.starting_node.work_product]=self.starting_node
        product_arr = self.__add_to_array(product_arr,add_related(self.starting_node))
            
        completed_arr.append(self.starting_node.work_product)

        #initialize loop variables
        finished = False
        index = 0
        #need to build a list of products using the ancestry of the products.
        # loop through the product_arr for each product add the ancestors of 
        # the product into product_arr to process the ancestors of that product
        # meanwhile add the direct parents of each product to the dictionary 'network'
        while finished == False:
            if index >= len(product_arr):
                finished = True
            elif product_arr[index] not in completed_arr:
                product = product_arr[index]
                temp = product.split(", ")
                t_node = node(temp[0].strip(),temp[1].strip())
                #checkindates[product] = t_node.checkindate

                if product not in network.keys():
                    network[product] = t_node
                product_arr = self.__add_to_array(product_arr,add_related(t_node))

                arr_count = len(product_arr)

                completed_arr.append(product)
            index += 1
        return network   
#---------------------end class nodes--------------------------

#--------------------------------------------------------------
# plot_obj
#   dd: network/children/ancestors data from Nodes
class plot_obj:
    def __init__(self,dd):
        self.data_dict = dd
        
        #keep order of below, or overwrites may happen
        #----instantiate private variables
        self._production_arr = []
        self._prodsizes_arr = []
        self._test_arr = []
        self._testsizes_arr = []
        #----set defaults keep order or automatic processes may fail
        self.process = 'parents'
        self.graph_type = 'digraph'
        self.layout = 'spring'
    @property
    def process(self):
        return self._process
    @process.setter
    def process(self,value):
        #set
        if value in ['parents','children','all']:
            self._process = value
    @property
    def production_arr(self):
        return self._production_arr
    @production_arr.setter
    def production_arr(self,value):
        self._production_arr = value
    @property
    def prodsizes_arr(self):
        return self._prodsizes_arr
    @prodsizes_arr.setter
    def prodsizes_arr(self,value):
        self._prodsizes_arr = value
    @property
    def test_arr(self):
        return self._test_arr
    @test_arr.setter
    def test_arr(self,value):
        self._test_arr = value
    @property
    def testsizes_arr(self):
        return self._testsizes_arr
    @testsizes_arr.setter
    def testsizes_arr(self,value):
        self._testsizes_arr=value
    @property
    def graph_type(self):
        return self._graph_type
    @graph_type.setter
    def graph_type(self, value):
        if value.lower() == 'graph':
            self.__nx_graph= nx.Graph()
        elif value.lower() == 'digraph':
            self.__nx_graph= nx.DiGraph()
            self.__build_directed_network()

        self._graph_type = value
    @property
    def layout(self):
        return self._layout
    @layout.setter
    def layout(self,value):
        if value == 'circular':
            self.__pos = nx.circular_layout(self.__nx_graph)
        elif value == 'shell':
            self.__pos = nx.shell_layout(self.__nx_graph)
        elif value == 'spectral':
            self.__pos = nx.spectral_layout(self.__nx_graph)
        elif value == 'spring':
            self.__pos = nx.spring_layout(self.__nx_graph, k=1, iterations=50)
        else:
            self.__pos = nx.random_layout(self.__nx_graph)
            value = 'random'
        self._layout = value
    @property
    def d3_json(self):
        #ToDo
        #Add positional data to nodes in json
        data = self.__build_d3_json()

        return json.dumps(data)

    #------------------------------------------------
    #- format the product name as product, version, status

    def __format_display_f1(self, p1):
        return "{}".format(p1)
    def __format_display_f2(self, p1,p2):
        return "{}, {}".format(p1,p2)
    def __format_display_f3(self, p1,p2,p3):
        return "{}, {}, {}".format(p1,p2,p3)
    #------------------------------------------------
    #- create json output for d3
    def __build_d3_json(self):
        temp_data = json_graph.node_link_data(self.__nx_graph)
        data_dict = {}
        link_arr = []
        for row in temp_data['nodes']:
            row['x'] = self.__pos[row['id']][0] * 1000
            row['y'] = self.__pos[row['id']][1] * 1000
            row['title'] = row['id']
            data_dict[row['id']] = row
        for row in temp_data['links']:
            t_dict = {}
            t_dict['source'] = data_dict[row['source']]['id']
            t_dict['target'] = data_dict[row['target']]['id']
            link_arr.append(t_dict)
        temp_data['links'] = link_arr
        print(temp_data)
        return temp_data
    #------------------------------------------------
    #- build network dat
    def __build_directed_network(self):
        for key in self.data_dict.keys():
            cur_node = self.data_dict[key]
            t_split = key.split(", ")
            f_key = self.__format_display_f2(t_split[0].strip(),t_split[1].strip())
            if f_key not in self.__nx_graph.nodes:
                self.__nx_graph.add_node(f_key,
                                         checkindate=cur_node.checkindate, 
                                         num_inputs=len(cur_node.parents),
                                         num_outputs=len(cur_node.children))
            if t_split[2].strip().lower() == 'prod':
                self.prodsizes_arr.append(200 * len(cur_node.parents))
                self.production_arr.append(f_key)
            elif t_split[2].strip().lower() == 'test':
                self.testsizes_arr.append(200 * len(cur_node.parents))
                self.test_arr.append(f_key)
            #add edges for parents
            if self.process in ['parents','all']:
                for product in cur_node.parents:
                    t_split = product.split(', ')
                    f_product = self.__format_display_f2(t_split[0].strip(),t_split[1].strip())
                    if f_product not in self.__nx_graph.nodes:
                        self.__nx_graph.add_node(f_product,
                                                 checkindate=self.data_dict[product].checkindate, 
                                                 num_inputs=len(self.data_dict[product].parents),
                                                 num_outputs=len(self.data_dict[product].children))
                    self.__nx_graph.add_edge(f_product, f_key)
            #add edges for children
            if self.process in ['children','all']:
                for product in cur_node.children:
                    t_split = product.split(', ')
                    f_product = self.__format_display_f2(t_split[0].strip(),t_split[1].strip())
                    if f_product not in self.__nx_graph.nodes:
                        self.__nx_graph.add_node(f_product,
                                                 checkindate=self.data_dict[product].checkindate, 
                                                 num_inputs=len(self.data_dict[product].parents),
                                                 num_outputs=len(self.data_dict[product].children))
                    self.__nx_graph.add_edge(f_key,f_product)


    #--------------------------------------------------------------
    #- build directed plot
    def build_plot(self):
    
        #nx.draw_networkx_nodes(G,pos, nodelist=G.nodes,node_size=[(len(G.edges(v))+1) * 50 for v in G.nodes])

        #set Production level nodes to green and adjust size by how many edges start from each node
        nx.draw_networkx_nodes(self.__nx_graph, 
                               self.__pos, 
                               nodelist=self.production_arr, 
                               node_color='g', 
                               node_size=[(len(self.__nx_graph.edges(v))+1) * 50 for v in self.production_arr])
        #set Test level nodes to red and adjust size by how many edges start from each node
        nx.draw_networkx_nodes(self.__nx_graph,
                               self.__pos, 
                               nodelist=self.test_arr, 
                               node_color='r',
                               node_size=[(len(self.__nx_graph.edges(v))+1) * 50 for v in self.test_arr])
        #Draw edges between nodes with directional arrows
        options = {
            'width': .5,
            'arrowstyle': '-|>',
            'arrowsize': 12
        }
        nx.draw_networkx_edges(self.__nx_graph, self.__pos, arrows=True, **options)
    
        # raise text positions to be above the nodes then draw the labels
        for p in self.__pos:  
            self.__pos[p][1] += 0.05 
        nx.draw_networkx_labels(self.__nx_graph, self.__pos,font_size=9)    

        # write in UTF-8 encoding
        #with open("edgelist.utf-8", "wb") as fh:
        #    nx.write_multiline_adjlist(self.__nx_graph, fh, delimiter="\t", encoding="utf-8")
        # read and store in UTF-8
        #fh = open("edgelist.utf-8", "rb")
        #H = nx.read_multiline_adjlist(fh, delimiter="\t", encoding="utf-8")
        # write nodes and edges to file
        #data = json_graph.node_link_data(self.__nx_graph)
        #self._plot_json = data
        #with open("data.json", "w") as fh:
        #    json.dump(data,fh)
        


        #use MATPLOTLIB to display the plot.
        plt.show()
#---------------------end class plot_obj--------------------------   


#------------------------------------------------
#-build the plot
#   workProduct:    product name
#   version:        product version
#   network_type:   'ancestors' = process only ancestors of the product/version, 
#                   'children' = process only children of the product/version, 
#                   'all' = process only ancestors and children of all products related to the product/version
#   build:          'data' = only build the json data of the graph
#                   'plot' = build json data and create plot
#   layout:         plot layout valid values: 'circular','specular','spring','shell','random'
def build_plot(workProduct, version, network_type, build='data', layout='spring'):
    #create nodes class
    network = nodes(args.workProduct.upper(), args.version)

    data = None
    #get data from nodes class
    if network_type.lower() == 'ancestors':
        data = network.ancestors
    elif network_type.lower() == 'children':
        data = network.children
    elif network_type.lower() == 'all':
        data = network.network
    else:
        raise ValueError ('Invalid Network value: {}'.format(network_type))
    #create plot_obj class
    plots = plot_obj(data)
    #define layout of plot
    plots.layout = layout.lower()
    #display plot
    if build == 'plot':
        plots.build_plot()
    #write json file and return json to calling application 
    d3_json = plots.d3_json
    filename = '{}_{}_{}.json'.format(workProduct,version,network_type)
    with open(filename, "w") as fh:
        json.dump(d3_json,fh)
    return d3_json

#------------------------------------------------
#- define arguments for build_plot (if run manually)
def make_argparse():
    parser = argparse.ArgumentParser(
            description=(
                "Get Ancestors/children of a product and build a graph to display the data"
                )
            )  
    parser.add_argument(
        'workProduct', type=str, 
        help=("The name of the target Work Product; for example 'HSDB'"
            )
    )
    parser.add_argument(
        'version', type=str,
        help=(
            "The version number (should start with the letter 'v'); for example, 'v1.0'"
            )
    )
    parser.add_argument(
        '-l', '--layout', type=str, default='spring',
        help=(
            "layout of the graph, valid values: circular, shell, spectral, spring.   Defualt is spring"
            )
    )
    parser.add_argument(
        '-n', '--network', type=str, default='ancestors',
        help=(
            "what direction to build from (trace children, ancestors, or both) use children, ancestors or all. .  valid values: children, ancestors, all.  Default is ancestors"
            )
    )
    parser.add_argument(
        '-b', '--build', type=str, default='data',
        help=(
            "Build and return data (json) only or data and plot .  valid values: data, plot.  Default is data"
            )
    )
    return parser

#------------------------------------------------
#- manual run of build_plot
if __name__=="__main__":
    parser= make_argparse()
    args = parser.parse_args()

    build_plot(args.workProduct, args.version, args.network, args.build, args.layout)

    #p='CIENFAHSSMPF'
    #v='v1.0'
    #p='MAXSUMDOSE'
    #v='v2.0'
    #p='MFGRID'
    #v='v8.3'
    #p='PHPROP'
    #v='v3.7'
    #p='HSSMCA'
    #v='v1.1'
    #p='SRI2SZ'
    #v='v1.0a'
    #p='CIENFA2018'
    #v='v1.1'