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

## Tool Guidlines
- use a config file (as a .json)
  - the config module can help
  - use the argument parser here, too. 


