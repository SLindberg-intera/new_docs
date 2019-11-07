"""
    Generate the 'graph'  (nodes and connections)
        for the ICF blockchain

    a graph is comprised of Nodes and Connections

    Nodes represent the ICF data work products
        (a WorkProductVersion instance)

    Connections represent relationships between two Nodes 


    this data will be used to create visualizations

This tool depends on two other modules:

  pylib\fingerprint
  pylib\backbone

"""
import sys, os
import argparse
from constants import ICF_HOME
import datetime
import itertools
import json

NODES_KEY = 'Nodes'
CONNECTIONS_KEY = 'Connections'
DATE_KEY = 'Date'

try:
    from backbone import backbone

except (ImportError, ModuleNotFoundError):
    reporoot = os.path.abspath(
        os.path.join(os.path.abspath(__file__), '..','..'))
    if reporoot not in sys.path:
        sys.path.append(reporoot)
    from backbone import backbone

from show_all import show_all     

def get_date():
    return str(datetime.datetime.now())

def work_product_name_to_id(name, version):
    return "_".join([name, version])


def work_product_to_node(work_product):
    connections = work_product.block.connections
    return {"node":
            {
            "id":work_product_name_to_id(work_product.work_product_name,
                work_product.version_str),
            "name":work_product.work_product_name,
            "version":work_product.version_str,
            "qa_status":work_product.qa_status,
            "path":work_product.path,
            "fingerprint":work_product.fingerprint,
            "timestamp":work_product.timestamp,
            "parents":[work_product_name_to_id(
                    item.work_product_name, item.version_str) 
                        for item in work_product.parents
                ]
            },
            "connections":connections
            }


def blockpath_to_work_product_id(inpath):
    root, last = os.path.split(inpath)
    root, last = os.path.split(root)
    root, version = os.path.split(root)
    root, name = os.path.split(root)
    return work_product_name_to_id(name, version)

def process_connection(connection_dict):
    source = connection_dict["source"]
    target = connection_dict["target"]
    source = blockpath_to_work_product_id(source)
    target = blockpath_to_work_product_id(target)
    return {"source":source, "target":target, 
            "value":connection_dict["value"],
            "id":"->".join([source, target])
            }

def get_network():
    alldata = list(map(work_product_to_node, show_all(as_str=False)))
    nodes= [item["node"] for item in alldata]
    connections = itertools.chain(
            *[list(map(lambda x:x.as_dict(), item["connections"])) 
                for item in alldata if item["connections"]])
    connections_raw = list(map(process_connection, connections))

    connections = []
    for connection in connections_raw:
        if connection["id"] in [c["id"] for c in connections]:
            continue
        connections.append(connection)

    return nodes, connections 



def assemble_dataset():
    nodes, connections = get_network()
    return {
            DATE_KEY: get_date(),
            NODES_KEY: nodes,
            CONNECTIONS_KEY: connections
            }

def make_argparse():
    parser = argparse.ArgumentParser(
            description=(
                "Write the ICF state as a JSON"
                )
            )
    parser.add_argument(
        'dirname', type=str, 
        help=("The path to where you want to output the result"
            ),
        default="."
    )
    return parser

if __name__=="__main__":
    parser = make_argparse()
    args = parser.parse_args()
    s = json.dumps(assemble_dataset())
    with open(os.path.join(args.dirname, "icfdata.json"), "w") as f:
        f.write(s)

