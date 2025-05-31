# Running on the Command Line

## Synopsis

```cmd
python src\grebakker.py backup f:\backup\2025_05 d:\
```


## Help screen

```cmd
usage: grebakker [-h] [-c FILE] [--version] [--continue] [--log-name LOG_NAME]
                 [--log-restart] [--log-off] [--log-format LOG_FORMAT]
                 [-e FILE] [-v]
                 action destination definition

greyrat's backupper for hackers

positional arguments:
  action
  destination
  definition

options:
  -h, --help            show this help message and exit
  -c FILE, --config FILE
                        Reads the named configuration file
  --version             show program's version number and exit
  --continue            Continues a stopped backup.
  --log-name LOG_NAME   Change logfile name (default: 'grebakker_log.csv').
  --log-restart         An existing logfile will be removed.
  --log-off             Does not generate a log file.
  --log-format LOG_FORMAT
                        Select log format to use ['csv', 'json']
  -v, --verbose         Increases verbosity level (up to 2).

(c) Daniel Krajzewicz 2025
```

## Description

__grebakker__ performs one of the following actions: ```backup```. The ```backup``` action makes a backup of files and folders.

```destination``` defines the ___destination folder___ into which the backupped files will be stored into. ```definition``` is the path to a __grebakker__ definition file named ```grebakker.json```.

__grebakker__ writes a log file that lists what has been done. Per default, the log file is named ```grebakker_log.csv``` and is written into the current working directory. After __grebakker__ has finished backupping, the file is moved to the ___destination folder___. The name of the log file can be changed using the option **--log-name *&lt;LOG_NAME&gt;***. If the option **--log-restart** is set, an existing log file will be overwritten. If the option **--log-off** is set, no log file will be generated. One may define the format of the log file using the option **--log-format *&lt;LOG_FORMAT&gt;***. Currently, the available formats are ```csv``` and ```json```.

__grebakker__ will complain if a log file with the defined / default name already exists and neither the option **--log-restart** nor the option **--continue** is set, assuming that a prior backup has failed. You should check the existing log file for errors in such cases. If the option **--continue** is set, __grebakker__ will skip backups already existing in the target folder and append the performed actions to an optionally existing log file.

The option **--verbose** (or **-v** for short) increaes the verbosity level. Currently, the highest verbosity level is 2.

When **--help** (or **-h**) is set, the help screen will be printed and __grebakker__ will exit afterwards.

When **--version** is set, a version information will be printed and __grebakker__ will exit afterwards.


## Examples

```cmd
python src\grebakker.py backup f:\backup\2025_05 d:\
```

Will backup files into the destination folder ```f:\backup\2025_05``` using the definition ```grebakker.json``` located in ```d:\```.

## Command line arguments and options

### Positional arguments

* **action**: The action to perform. Currently available actions are: ```backup```
* **destination**: The destination folder to backup the files into
* **definition**: The backup definition to use

### Options

* **-h** / **--help**: Shows the help screen
* **-c *&lt;FILE&gt;*** / **--config *&lt;FILE&gt;***: Reads the named configuration file
* **--version**: show program's version number and exit
* **--continue**: Continues a stopped backup.
* **--log-name *&lt;LOG_NAME&gt;***: Change logfile name (default: 'grebakker_log.csv').
* **--log-restart**: An existing logfile will be removed.
* **--log-off**: Does not generate a log file.
* **--log-format *&lt;LOG_FORMAT&gt;***: Select log format to use ['csv', 'json']
* **-v** / **--verbose**: Increases verbosity level (up to 2).
