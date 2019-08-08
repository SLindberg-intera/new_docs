# Runner

This script acts as a controller for all of the other utilities contained within this code database.


## Example:
### Getting help
```console
python pylib\runner\runner.py --help
```

### Running a CACIE tool with arguments:

Note the program name and arguments must be in quotes.
```console
python pylib\runner\runner.py "program name" "program arguments"
```
For example, to run the data reducer in help mode:
``` console
python pylib\runner\runner.py "python" "pylib\vzreducer\reducer.py --help"
```
Example: to execute runner / hssmbuilder from outside git repository:
```console
python ..\..\ca-cie-tools\CA-CIE-Tools\pylib\runner\runner.py "python" "..\..\ca-cie-tools\CA-CIE-Tools\pylib/hssmbuilder/build_hssm_0.1.py config_tc-99.json" --gitpath "..\..\CA-CIE-tools\CA-CIE-Tools\.git" --logfile "tc-99_hssm_pkg.txt"
```

## Tool Guidlines
- use a config file (as a .json)
  - the config module can help
  - use the argument parser here, too. 


