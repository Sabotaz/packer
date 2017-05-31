#!/usr/bin/python

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import os.path
import threading
#import re
#for branch reset feature:
import regex as re

lock = threading.Lock()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class ReloadSystemLib(Exception):
    pass
    
class ImportLib(metaclass=Singleton):
    wd = "."
    def __init__(self):
        self.libs = []
        self.loaded_libs = []
        
    def load(self, lib):
        if lib not in self.loaded_libs:
            if lib in self.libs:
                raise ReloadSystemLib()
            self.libs.append(lib)
            yield from Source(lib).process()
            self.loaded_libs.append(lib)
            
    def clear(self):
        ImportLib.__init__(self)
        
class Source:
    def __init__(self, name):
        self.requierments = []
        self.name = name
        
    def process(self):
        with open(ImportLib.wd + "/" + self.name + ".py", 'r') as infile:
            yield from self.process_file(infile)
            
    def process_file(self, infile):
        for line in infile:
            import_regexp = re.compile(r"(?|import (\w+)|from (\w+) import \*)")
            import_statement = re.search(import_regexp, line)
            if import_statement:
                cible = import_statement.group(1)
                try:
                    yield from ImportLib().load(cible)
                    self.requierments.append(cible)
                except IOError:
                    yield line
                except ReloadSystemLib:
                    pass
            else:
                for lib in self.requierments:
                    if lib + "." in line:
                        line = line.replace(lib + ".", "")
                yield line

def recompile(wd):
    lock.acquire()
    ImportLib().clear()
    ImportLib.wd = wd
    
    with open('exange_file', 'w') as outfile:
        for line in ImportLib().load("main"):
            outfile.write(line)
    lock.release()


class Handler(FileSystemEventHandler):
    def __init__(self, cible):
        FileSystemEventHandler.__init__(self)
        self.directory = cible

    def on_deleted(self, event):
        print(event)
        recompile(self.directory)

    def on_modified(self, event):
        if event.event_type != "DirModifiedEvent":
            print(event)
            recompile(self.directory)

    def on_moved(self, event):
        print(event)
        recompile(self.directory)

if __name__ == "__main__":
    directory = input()
    event_handler = Handler(directory)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    recompile(directory)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

