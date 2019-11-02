"""

This tool depends on two other modules:

  pylib\fingerprint
  pylib\backbone

"""
import sys, os
from constants import ICF_HOME

ICF_HOME = os.path.join(
        "S:/","PSC","!HANFORD","ICF","TEST")

try:
    from backbone import backbone

except ModuleNotFoundError:
    reporoot = os.path.abspath(
        os.path.join(os.path.abspath(__file__), '..','..'))
    if reporoot not in sys.path:
        sys.path.append(reporoot)
    from backbone import backbone


def summarize_version(work_product, version):
    path = os.path.join(ICF_HOME, work_product, version)
    if os.path.exists(path):
        summary = backbone.WorkProductVersion.explain_version(path)
        return summary
    raise ValueError("Could not find Work Product '{} {}'".format(work_product, version))
        



if __name__=="__main__":
    work_product = sys.argv[1]
    version = sys.argv[2]

    print(summarize_version(work_product, version))
