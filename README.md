# Packer
This script join multiple python files into one.

It is use for developping on CodinGame Plateform on multiple files, when using [CodinGame Sync](https://www.codingame.com/forum/t/codingame-sync-beta/614).
```
$ python3 watcher.py
path/to/my/codingame/project/folder
```
It uses the file `main.py`, then crawls on the import statements and includes the content of imported files (if exists) instead.

The global file is wrote in `exange_file`, who then can then be used by CodinGame Sync.

Each time a modification is done in the project path, the crawler rebuild the `exange_file`.

Used with CodinGame Sync, it is automatically pushed on CodinGame at each modification.