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


def summarize_version():
    path = os.path.join(ICF_HOME)
    for work_product in os.listdir(path):
        wppath = os.path.join(path, work_product)
        wp = backbone.WorkProduct(wppath)
        versions = wp.versions
        if len(versions)>0:
            s = "{} {}".format(str(wp), 
                    "  ".join(map(lambda x: x.version_str, wp.versions))
                    )
            yield s

if __name__=="__main__":
    print("\n".join(summarize_version()))
