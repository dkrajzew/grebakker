#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""grebakker - greyrat's backupper for hackers
"""
# ===========================================================================
__author__     = "Daniel Krajzewicz"
__copyright__  = "Copyright 2025, Daniel Krajzewicz"
__credits__    = "Daniel Krajzewicz"
__license__    = "GPL"
__version__    = "0.2.0"
__maintainer__ = "Daniel Krajzewicz"
__email__      = "daniel@krajzewicz.de"
__status__     = "Development"
# ===========================================================================
# - https://github.com/dkrajzew/grebakker
# - http://www.krajzewicz.de
# ===========================================================================


# --- imports ---------------------------------------------------------------
import json
import sys
import os
import datetime
import argparse
import configparser
import shutil
import errno
import zipfile
import pathlib
import fnmatch
from typing import List
from typing import Dict
from typing import Any


# --- class definitions -----------------------------------------------------
class Log:
    def __init__(self, name, restart, log_format, off):
        self._format = log_format
        self._written = 0
        self._output = None
        self._name = name
        if off: return
        mode = "w" if restart else "a"
        self._output = open(name, mode)
        if self._format=="json":
            self._output.write(f'[\n')

    def write(self, act, src, dst, duration):
        if self._output is None:
            return
        if self._format=="csv":
            self._output.write(f'"{act}";"{src}";"{dst}";"{duration}"\n')
        elif self._format=="json":
            if self._written!=0:
                self._output.write(',\n')
            self._output.write('    {"action": "' + act + '", "src": "' + src + '", "dst": "' + dst + '", "duration": "' + duration + '"}')
        self._output.flush()
        self._written += 1
        
    def close(self):
        if self._output is None:
            return
        if self._format=="json":
            self._output.write(f'\n]\n')
        self._output.close()
        

class Grebakker:
    def __init__(self, dest, log, verbosity):
        self._dest = dest
        self._log = log
        self._verbosity = verbosity
        self._line_ended = True

    
    def report(self, act, src, dst, duration):
        self._log.write(act, src, dst, duration)

    
    def action_begin(self, mml_action, path, level):
        if self._verbosity>1:
            print(f"{self._i(level+1)}{mml_action} '{path}'... ", end="", flush=True)
            self._line_ended = False
        return datetime.datetime.now()


    def action_end(self, action, path, dst, level, t1):
        t2 = datetime.datetime.now()
        self.report(action, path, dst, str(t2-t1))
        if self._verbosity>1:
            print(f"done. ({t2-t1})")
            self._line_ended = True

    def _yield_files(self, src, exclude):
        for root, dirs, files in os.walk(src):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file in files:
                srcf = os.path.relpath(os.path.join(root, file), src)
                use = True
                #print(f"{exclude}")
                for e in exclude:
                    if fnmatch.fnmatchcase(srcf, e):
                        #print(f"{srcf} {e}")
                        use = False
                        break
                #print(f"{file} {use}")
                if not use:
                    continue
                #print(f"!!! {file}")
                yield os.path.relpath(os.path.join(root, file), os.path.join(src, ".."))

    
    def _i(self, level):

        return ' '*level
    
    def get_destination(self, action, src, dst_root, path, extension, level):
        dst = os.path.join(dst_root, path) + extension
        #print(f"dst {dst}")
        if os.path.exists(dst):
            self.report(action, src, dst, "skipped")
            if self._verbosity>1:
                if not self._line_ended:
                    print()
                    self._line_ended = True
                print(f"{self._i(level+1)}Skipping '{dst}' - exists.")
            return None
        return dst


    def copy(self, src_root, item, dst_root, level):
        path = item if type(item)==str else item["name"]
        exclude = [] if type(item)==str or "exclude" not in item else item["exclude"]
        exclude = [exclude] if type(exclude)==str else exclude
        src = os.path.join(src_root, path)
        if not os.path.exists(src):
            raise ValueError(f"file/folder '{src}' to copy does not exist")
        if os.path.isfile(src):
            dst = self.get_destination("copy", src, dst_root, path, "", level)
            if dst is None:
                return
            t1 = self.action_begin("Copying", src, level)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            self.action_end("copy", src, dst, level, t1)
        else:
            t1 = self.action_begin("Copying", src, level)
            dst = os.path.join(dst_root, path)
            for file in self._yield_files(src, exclude):
                fdst = self.get_destination("copy", os.path.join(src, file), dst_root, file, "", level+1)
                if fdst is None:
                    continue
                fsrc = os.path.join(src, "..", file)
                os.makedirs(os.path.dirname(fdst), exist_ok=True)
                shutil.copy(fsrc, fdst)
            self.action_end("copy", src, dst, level, t1)
        

    def compress(self, root, item, dst_root, level):
        path = item if type(item)==str else item["name"]
        exclude = [] if type(item)==str or "exclude" not in item else item["exclude"]
        exclude = [exclude] if type(exclude)==str else exclude
        src = os.path.join(root, path)
        if not os.path.exists(src):
            raise ValueError(f"file/folder '{src}' to compress does not exist")
        dst = self.get_destination("compress", src, dst_root, path, ".zip", level)
        if dst is None:
            return
        t1 = self.action_begin("Compressing", src, level)
        zipf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=9)
        if os.path.isfile(src):
            dstf = os.path.relpath(src, os.path.join(src, '..'))
            zipf.write(src, dstf)
        else:
            for file in self._yield_files(src, exclude):
                fsrc = os.path.join(src, "..", file)
                dstf = os.path.relpath(os.path.join(root, file), os.path.join(src, '..'))
                zipf.write(fsrc, dstf)
        zipf.close()
        self.action_end("compress", src, dst, level, t1)

        
    def backup(self, root, level=0):
        # init
        if self._verbosity>0:
            print(f"{self._i(level)}Processing '{root}'...")
            self._line_ended = True
        definition = None
        with open(os.path.join(root, "grebakker.json"), encoding="utf-8") as fd:
            definition = json.load(fd)
        dst_path = os.path.join(self._dest, definition["destination"])
        os.makedirs(dst_path, exist_ok=True)
        # copy
        to_copy = [] if "copy" not in definition else definition["copy"]
        for path in to_copy:
            self.copy(root, path, dst_path, level)
        # compress
        to_compress = [] if "compress" not in definition else definition["compress"]
        for path in to_compress:
            self.compress(root, path, dst_path, level)
        # subfolders
        subs = [] if "subfolders" not in definition else definition["subfolders"]
        for sub in subs:
            path = sub if type(sub)==str else sub["name"]
            src = os.path.join(root, path)
            if not os.path.exists(src):
                raise ValueError(f"file/folder '{src}' to recurse into does not exist")
            dst = self.get_destination("sub", src, dst_path, path, "", level)
            if dst is None:
                continue
            self._log.write("sub", src, dst, "0:00:00")
            self.backup(os.path.join(root, sub), level+1)
        shutil.copy(os.path.join(root, "grebakker.json"), dst_path)
        if level==0:
            self._log.close()
            if self._log._written!=0:
                shutil.move(self._log._name, os.path.join(dst_path, self._log._name))

"""
    def restore(self, root, level=0):
        # init
        if self._verbosity>0:
            print(f"{self._i(level)}Processing {root}...")
        definition = None
        with open(os.path.join(root, "grebakker.json"), encoding="utf-8") as fd:
            definition = json.load(fd)
        exit()
        dst_path = os.path.join(self._dest, definition["destination"])
        os.makedirs(dst_path, exist_ok=True)
        # copy
        to_copy = [] if "copy" not in definition else definition["copy"]
        for path in to_copy:
            self.copy(root, path, dst_path, level)
        # compress
        to_compress = [] if "compress" not in definition else definition["compress"]
        for path in to_compress:
            self.compress(root, path, dst_path, level)
        # subfolders
        subs = [] if "subs" not in definition else definition["subs"]
        for sub in subs:
            self.backup(os.path.join(root, sub), level+1)
        shutil.copy(os.path.join(root, "grebakker.json"), dst_path)
        self._log.close()
        if self._log._written!=0:
            shutil.move(self._log._name, os.path.join(dst_path, self._log._name))
"""


# --- functions -------------------------------------------------------------
def main(arguments : List[str] = None) -> int:
    """
    The main method using parameters from the command line.

    Args:
        arguments (List[str]): A list of command line arguments.

    Returns:
        (int): The exit code (0 for success).
    """
    # parse options
    # https://stackoverflow.com/questions/3609852/which-is-the-best-way-to-allow-configuration-options-be-overridden-at-the-comman
    defaults = {}
    conf_parser = argparse.ArgumentParser(prog='grebakker', add_help=False)
    conf_parser.add_argument("-c", "--config", metavar="FILE", help="Reads the named configuration file")
    args, remaining_argv = conf_parser.parse_known_args(arguments)
    if args.config is not None:
        if not os.path.exists(args.config):
            print ("grebakker: error: configuration file '%s' does not exist" % str(args.config), file=sys.stderr)
            raise SystemExit(2)
        config = configparser.ConfigParser()
        config.read([args.config])
        defaults.update(dict(config.items("grebakker")))
    parser = argparse.ArgumentParser(prog='grebakker', parents=[conf_parser],
                                     description="greyrat's backupper for hackers",
                                     epilog='(c) Daniel Krajzewicz 2025')
    parser.add_argument("action", default="backup")
    parser.add_argument("destination")
    parser.add_argument("definition", default="grebakker.json")
    parser.add_argument('--version', action='version', version='%(prog)s 0.2.0')
    parser.add_argument('--continue', dest="cont", action="store_true", help="Continues a stopped backup.")
    parser.add_argument('--log-name', default="grebakker_log.csv", help="Change logfile name (default: 'grebakker_log.csv').")
    parser.add_argument('--log-restart', action="store_true", help="An existing logfile will be removed.")
    parser.add_argument('--log-off', action="store_true", help="Does not generate a log file.")
    parser.add_argument('--log-format', default="csv", choices=['csv', 'json'], help="Select log format to use ['csv', 'json']")
    """
    parser.add_argument('--compress-max-size', default="2g", help="Defines maximum archive size (default: 2g).")
    parser.add_argument('--compress-max-size-abort', action="store_true", help="Stop when an archive is bigger than the maximum size.")
    parser.add_argument('--compress-max-threads', type=int, default=1, help="Defines maximum thread number.")
    """
    #parser.add_argument('-e', '--excluded-log', metavar="FILE", default=None, help="Writes excluded files and folders to FILE.")
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Increases verbosity level (up to 2).") # https://stackoverflow.com/questions/6076690/verbose-level-with-argparse-and-multiple-v-options
    parser.set_defaults(**defaults)
    args = parser.parse_args(remaining_argv)
    verbosity = int(args.verbose)
    # check
    errors = []
    if args.action not in ["backup"]:
        errors.append(f"unkown action '{args.action}'")
    if len(errors)!=0:
        for e in errors:
            print(f"grebakker: error: {e}", file=sys.stderr)
        raise SystemExit(2)
    #
    if os.path.exists(args.log_name):
        if not args.cont and not args.log_restart:
            print("grebakker: error: a log file exists, but it is not defined whether to restart or to continue.", file=sys.stderr)
            raise SystemExit(2)
        if args.cont:
            print("A log file exists; contents will be appended.")
        if args.log_restart:
            print("The existing log file will be replaced by new contents.")
    if not os.path.exists(args.destination):
        os.makedirs(args.destination, exist_ok=True)
    #
    ret = 0
    if verbosity>0:
        print("Starting...")
    t1 = datetime.datetime.now()
    log = Log(args.log_name, args.log_restart, args.log_format, args.log_off)
    grebakker = Grebakker(args.destination, log, verbosity)
    if args.action=="backup":
        try:
            grebakker.backup(args.definition)
        except ValueError as e:
            print(f"grebakker: error: {e}.", file=sys.stderr)
            ret = 2
    t2 = datetime.datetime.now()
    if verbosity>0 and ret==0:
        print(f"Completed after {(t2-t1)}")
    return ret


# -- main check
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:])) # pragma: no cover




