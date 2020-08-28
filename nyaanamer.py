import os
import re
import path_handler

EXTENSION_REGEX = r"\.?(\w+)"

def only_ignore_handler(path, only="", ignore=""):
    """Returns a list of files and directories in a path after filtering them according to the
    conditions in the argument. "only" has more priority than "ignore". By default they're empty strings
    """
    files = os.listdir(path)
    if only:
        only = ["."+extension for extension in re.findall(EXTENSION_REGEX, only)]
        if '.directory' in only:
            only.remove('.directory')   # Removing ".directory" to ensure smooth filtering of files with extensions
            directories = [f for f in files if os.path.isdir(os.path.join(path, f))]    # sorts out the directories
            files = [f for f in files if f.endswith(tuple(only))] + directories
        else:
            files = [f for f in files if f.endswith(tuple(only))]

    elif ignore:
        ignore = ["."+extension for extension in re.findall(EXTENSION_REGEX, ignore)]
        if '.directory' in ignore:
            ignore.remove('.directory') # Removing ".directory" to ensure smooth filtering of files with extensions
            directories = [f for f in files if os.path.isdir(os.path.join(path, f))]    # sorts out the directories
            files = [f for f in files if not f.endswith(tuple(ignore)) and f not in directories]
        else:
            files = [f for f in files if not f.endswith(tuple(only))]

    return files

def renamed_name(path, regex, replacewith, **kwargs):
    """Returns a list consisting tuple of original name and renamed name of the files filtered according to regex
    in a specific path provided in the argument. Keyword arguments are only and ignore which are both empty strings
    by default.
    """
    # PLAN: Add safe mode so that regex doesn't mess with extension
    gex = re.compile(regex)
    files = only_ignore_handler(path, kwargs.get('only', ""), kwargs.get('ignore', ""))
    original_and_renamed_name = [(x, gex.sub(replacewith, x)) for x in files]

    return original_and_renamed_name
        
print(renamed_name(r"D:\Programming\Training\test", r"\d", "LOL"))