#!/usr/bin/python

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import os.path
import threading

lock = threading.Lock()

def comp(wd, f, imports):
    print "compile", f
    lines = []
    with open(wd + "/" + f, 'r') as infile:
        for line in infile:
            if line.startswith("import "):
                cible = line[7:].rstrip()
                if cible in imports:
                    continue
                imports.add(cible)
                if os.path.isfile(wd + "/" + cible + ".py"):
                    lines.extend(comp(wd, cible + ".py", imports))
                else:
                    lines.append(line)
            else:
                lines.append(line)
    return lines

def recompile(wd):
    lock.acquire()
    main = comp(wd, "main.py", set())
    with open('exange_file', 'w') as outfile:
        for line in main:
            outfile.write(line)
    lock.release()


class Handler(FileSystemEventHandler):
    def on_deleted(self, event):
        print event
        recompile("src")

    def on_modified(self, event):
        if event.event_type != "DirModifiedEvent":
            print event
            recompile("src")

    def on_moved(self, event):
        print event
        recompile("src")

if __name__ == "__main__":
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, "src", recursive=True)
    recompile("src")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

