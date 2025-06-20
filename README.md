# grebakker

[![License: GPL](https://img.shields.io/badge/License-GPL-green.svg)](https://github.com/dkrajzew/grebakker/blob/master/LICENSE)
![test](https://github.com/dkrajzew/grebakker/actions/workflows/test.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/dkrajzew/grebakker/badge.svg?branch=main)](https://coveralls.io/github/dkrajzew/grebakker?branch=main)
[![Dependecies](https://img.shields.io/badge/dependencies-none-green)](https://img.shields.io/badge/dependencies-none-green)


[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=GVQQWZKB6FDES)



## Introduction

__grebakker__ is a hacker's backup solution.

__grebakker__ uses json to define what should be backupped and how - copied or compressed. The json files can reference each other.

__grebakker__ does not need any external applications, libraries, or modules besides plain Python.

## Background

I backup all my projects frequently. Being bored of doing it manually, I wrote __grebakker__ for doing it for me.



## Usage

Generate a backup definition of what to do in json and store it in the folder as ```grebakker.json```:

```js
{
    "destination": "d/",
    "copy": [ 
        "document.pdf",
        "old_backups"
    ],
    "compress": [
        { "sub": "repository" },
        { "sub": "current", "exclude": ["venv"] }
    ],
    "subs": [ "attic" ]
}
```

Then run __grebakker__:

```cmd
python src\grebakker.py backup f:\backup\2025_05 d:\
```

That's all... Your files and folders are backupped to the subfolder ```d/``` of the ___destination folder___ ```f:\backup\2025_05``` - the file ```document.pdf``` and the folder ```old_backups``` are copied to the destination ```f:\backup\2025_05\d```, the folder ```repository``` and ```current``` are compressed (excluding the sub-folder ```venv``` in ```current```) and stored in ```f:\backup\2025_05\d``` as well. __grebakker__ continues with backupping using a backup definition stored in the sub-folder ```attic```.

You may find further information at the subpages here or at [the __grebakker__ documentation pages](https://grebakker.readthedocs.io/en/latest/).


## Changes

### Version 0.2.0 (to come)

* an initial version

The complete [ChangeLog](https://grebakker.readthedocs.io/en/latest/changes.) is included in [the __grebakker__ documentation pages](https://grebakker.readthedocs.io/en/latest/).


## License (GPL)

__grebakker__ is licensed under the [GPL license](LICENSE).



## Status

__grebakker__ is in an early development stage. I suppose I will extend it in the future, but I am not under pressure.

Let me know if you need something by [adding an issue](https://github.com/dkrajzew/grebakker/issues) or by dropping me a mail.



## Contributing

I am very interested in opinions, ideas, etc. Please let me know.




