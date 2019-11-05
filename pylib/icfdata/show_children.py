"""

This tool depends on two other modules:

  pylib\fingerprint
  pylib\backbone

"""
import sys, os
import argparse
from constants import ICF_HOME


try:
    from backbone import backbone

except (ImportError, ModuleNotFoundError):
    reporoot = os.path.abspath(
        os.path.join(os.path.abspath(__file__), '..','..'))
    if reporoot not in sys.path:
        sys.path.append(reporoot)
    from backbone import backbone


def summarize_version(work_product, version):
    path = os.path.join(ICF_HOME, work_product, version)
    if os.path.exists(path):
        children = backbone.WorkProductVersion(path).children
        return "\n".join(map(lambda x: x.get_summary(), children))

    raise ValueError("Could not find Work Product '{} {}'".format(
        work_product, version))
        

def make_argparse():
    parser = argparse.ArgumentParser(
            description=(
                "Show the children of a particular ICF work product"
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
    return parser


if __name__=="__main__":
    parser= make_argparse()
    args = parser.parse_args()
    print(summarize_version(args.workProduct.upper(), args.version))
