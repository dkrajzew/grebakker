# Usage

## Outline

The idea is that you have one folder you want to store a backup of your files / folders into. This folder will be named ___destination folder___ in the following.

You may have multiple files / folders that shall be backupped. Most of those shall be compressed, but some may be already compressed or shall be kept as-are for any reason. That's why __grebakker__ supports both, copying and compressing files / folders.

In addition, you may want to define own backup rules for subfolders. E.g., you may have a folder where all your projects are located in. You could compress each project individually, but some may be too big for being stored in a single archive. Or you may want to exclude some files or folders in one part of the project, but not in another one. That's why __grebakker__ supports subfolders. 


## Basics

__grebakker__ backups files and folders into a destination folder. The files / folders to backup are either copied or compressed. In addition, __grebakker__ may walk through a hierarchy of folders to backup.

As such, __grebakker__ needs to know which files / folders shall be backupped and how. For each folder to backup, at least one definition file called ```grebakker.json``` is needed. This file uses JSON to define what shall be processed and how. Here is an example:


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
    "subfolders": [ "attic" ]
}
```

You will find the following information in it:

* ```destination``` is a subfolder in the global destination folder to save the backup into
* the (optional) attribute ```copy``` lists files and folders that shall be copied into the destination folder
* the (optional) attribute ```compress``` lists files and folders that shall be compressed; the generated archive is stored in the destination folder
* the (optional) attribute ```subfolders``` lists (sub)folders that shall be processed; in each of these folder, a new ```grebakker.json``` file must be given

The synopsis of grebakker is briefly

```cmd
python src\grebakker.py <ACTION> <DESTINATION> <SOURCE>
```

So given the file above, you may start __grebakker__ like this:

```cmd
python src\grebakker.py backup f:\backup\2025_05 d:\
```


Then, __grebakker__ reads the ```d:\grebakker.json``` file and copies all files / folders listed in the ```copy``` attribute, compresses all those listed in the ```compress``` attribute, and runs iteratively over all folders given in the ```subfolders``` attribute.


## Definition files

Take the example from above. For each project you want to backup, set up a file that describes how it shall be backupped - which files / folders shall be copied, which compressed and into which folders __grebakker__ shall dive into.


## Logging

__grebakker__ logs performed actions - either using the csv or the json format.

A csv file lists each action in a line, consisting of ***&lt;ACTION&gt;***;***&lt;SOURCE&gt;***;***&lt;DESTINATION&gt;***;***&lt;DURATION&gt;***. So a csv log file could look like this:

```csv
"copy";"document.pdf";"d/document.pdf";"0:00:01.11"
"copy";"old_backups";"d/old_backups";"0:01:02.2"
"compress";"repository";"d/repository.zip";"0:03:02.34545"
"compress";"current";"d/current.zip";"0:01:02.43242"
"sub";"attic";"d/attic";"0:00:00"
"compress";"attic/subfolder11";"d/attic/subfolder11.zip";"0:01:01.2398"
"compress";"attic/subfolder12";"d/attic/subfolder12.zip";"0:02:01.2342"
```

The json output stores the same information like '{ "action": "***&lt;ACTION&gt;***", "source": "***&lt;SOURCE&gt;***", "destination": "***&lt;DESTINATION&gt;***", "duration": "***&lt;DURATION&gt;***" }'.

```js
[
    { "action": "copy", "source": "document.pdf", "destination": "d/document.pdf", "duration": "0:00:0111" },
    { "action": "copy", "source": "old_backups", "destination": "d/old_backups", "duration": "0:01:02.2" },
    { "action": "compress", "source": "repository", "destination": "d/repository.zip", "duration": "0:03:02.34545" },
    { "action": "compress", "source": "current", "destination": "d/current.zip", "duration": "0:01:02.43242" },
    { "action": "sub", "source": "attic", "destination": "d/attic", "duration": "0:00:00" },
    { "action": "compress", "source": "attic/subfolder11", "destination": "d/attic/subfolder11.zip", "duration": "0:01:01.2398" },
    { "action": "compress", "source": "attic/subfolder11", "destination": "d/attic/subfolder12.zip", "duration": "0:02:01.2342" }
]
```

The log shall report what has been done. It may serve further purposes in the future.


## Safety

Well, ok, the thing is about backupping your files. This is important and it should work, right?

That's why __grebakker__ fails early and loud. After a successful backup, you should have the files located in your destination folder, including the backup definition files, and the log file. Only, and only if all these constraints are true (and __grebakker__ is not buggy, uh?), your backup was successful.

In any other cases __grebakker__ will complain with an error message and will stop the operation. It is then up to you to check the error messages and adapt needed actions.

BTW, I am paranoid here. I make a backup, extract the backupped files to a second folder and check whether all that shall be backupped was backupped. 


## How to start?

Yes, well, basically, you have to define a backup definition file for all the projects you want to back up and that's all... Run __grebakker__ on them.


## Any issues?

Yes, there are.

Currently, __grebakker__ does not report correctly when a folder was not copied or compressed completely. This must be changed in next versions.

As well, the tests - though covering almost 100% of the code - do not cover the compression of files well. This should be changed in the next steps as well.

