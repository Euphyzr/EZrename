import os
import re
import path_handler

def only_ignore_handler(path, only="", ignore=""):
    """Returns a list of files and directories in a path after filtering them according to the
    conditions in the argument. "only" has more priority than "ignore". By default they're empty strings"""
    files = os.listdir(path)
    if only:
        only = [c if c.startswith(".") else "."+c for c in only.split()]       # keeping this as a list for mutability
        if ".directory" in only:
            only.remove(".directory")
            directories = [f for f in files if os.path.isdir(os.path.join(path, f))]    # sorts out the directories
            files = [f for f in files if f.endswith(tuple(only))] + directories
        else:
            files = [f for f in files if f.endswith(tuple(only))]

    elif ignore:
        ignore = [c if c.startswith(".") else "."+c for c in ignore.split()]
        if ".directory" in ignore:
            ignore.remove(".directory")
            directories = [f for f in files if os.path.isdir(os.path.join(path, f))]
            files = [f for f in files if not f.endswith(tuple(ignore)) and f not in directories]
        else:
            files = [f for f in files if not f.endswith(tuple(only))]

    return files

def rename(path, regex, replacewith, only="", ignore=""):
    """Renames the files/directories filtered by only_ignore_handler by replacing the regex matches with
    provided [replacewith] argument"""
    gex = re.compile(regex)
    files = only_ignore_handler(path, only, ignore)

    for name in files:
        rename = gex.sub(replacewith, name)
        os.rename((os.path.join(path, name)), (os.path.join(path, rename)))

