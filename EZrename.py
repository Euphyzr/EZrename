import os
import re

EXTENSION_REGEX = r"\.?(\w+)"


def only_ignore_handler(path, only="", ignore=""):
    """Returns a list of files and directories in a path after filtering them according to the
    conditions in the argument. "only" has more priority than "ignore". By default they're empty strings
    """
    files = os.listdir(path)
    if only:
        # re.findall() expects string or byte-like object but parser returns list. so, " ".join() is called
        only = ["."+extension for extension in re.findall(EXTENSION_REGEX, " ".join(only))]
        if '.directory' in only:
            only.remove('.directory')  # Removing ".directory" to ensure smooth filtering of files with extensions
            directories = [f for f in files if os.path.isdir(os.path.join(path, f))]  # sorts out the directories
            files = [f for f in files if f.endswith(tuple(only))] + directories
        else:
            files = [f for f in files if f.endswith(tuple(only))]

    elif ignore:
        ignore = ["."+extension for extension in re.findall(EXTENSION_REGEX, " ".join(ignore))]
        if '.directory' in ignore:
            ignore.remove('.directory')
            directories = [f for f in files if os.path.isdir(os.path.join(path, f))]
            files = [f for f in files if not f.endswith(tuple(ignore)) and f not in directories]
        else:
            files = [f for f in files if not f.endswith(tuple(ignore))]

    return files


def renamed_name(path, replacewith, regex, **kwargs):
    """Returns a list consisting tuple of original name and renamed name of the files filtered according to regex
    in a specific path provided in the argument. Keyword arguments are only and ignore which are both empty strings
    by default.
    """
    files = only_ignore_handler(path, kwargs.get('only', ""), kwargs.get('ignore', ""))
    original_and_renamed_name = []

    for original_name in files:
        renamed = os.path.join(path, re.sub(regex, replacewith, original_name))
        original_name = os.path.join(path, original_name)
        original_and_renamed_name.append((original_name, renamed))

    return original_and_renamed_name


if __name__ == "__main__":
    import sys
    import argparse
    import path_handler
    import json_config_handler

    JSON_INDENT = 4
    PRESETS_LIMIT = 5
    NO_REGEX_MESSAGE = """
    No default regex is setted up. Use -d/--regex-default <regex> to setup a default regex.
    Alternatively, use -r/--regex <regex> to use a regex without a default one"""

    CONFIG_FLAGS = [
        '-d', '-ra', '-rd', '-rl', '-rc', '-u', '--regex-default', '--regex-add',
        '--regex-delete', '--regex-list', '--regex-clear', '--undo'
        ]
    def is_no_config_flags(flags=CONFIG_FLAGS):
        for flag in flags:
            if flag in sys.argv:
                return False
        return True
                    
    phandler = path_handler.PathHandler(invalid_turns=3, sys_exit=True)
    config_path = os.path.join((os.path.dirname(os.path.realpath(__file__))), "config.json")
    j = json_config_handler.JsonConfigHandler(config_path, JSON_INDENT)
    
    def restriction():
        sys.exit("Cannot have more than {} presets. Remove presets with -rd/--regex-delete [name]".format(PRESETS_LIMIT))
    j.on_restriction(restriction)

    
    parser = argparse.ArgumentParser(description="Bulk renames files and directories with handy options.")
    parser.add_argument('-p', '--path', help="path to files or directories", required=is_no_config_flags())
    parser.add_argument('-w', '--replacewith', help="matched regular expression pattern are replaced by this",
                                            required=is_no_config_flags())
    
    custom_regex = parser.add_mutually_exclusive_group()
    custom_regex.add_argument('-r', '--regex', help="matches regular expression pattern to replace it")
    custom_regex.add_argument('-pr', '--preset-regex', help="finds regex by name from presets to replace it.")

    parser.add_argument('-u', '--undo', action='store_true', help="undos the batch of rename")
    parser.add_argument('-q', '--quiet', action='store_true', help="doesn't display rename status")
    
    only_ignore = parser.add_mutually_exclusive_group()
    only_ignore.add_argument('-o', '--only', nargs='*', help="only matches for provided extension(s) as well as directory")
    only_ignore.add_argument('-i', '--ignore', nargs='*', help="ignores provided extension(s) as well as directory")
    
    config_args = parser.add_argument_group('config')
    config_args.add_argument('-d', '--regex-default', nargs='?', const=True, help="sets up a default regex to match by")
    config_args.add_argument('-rl', '--regex-list', action='store_true', help="lists all regex presets")
    
    config_args.add_argument('-ra', '--regex-add', nargs=2, metavar=('NAME', 'REGEX'),
                                                help="adds regex by name in regex presets. Multiworded name needs to be quoted")
    
    config_args.add_argument('-rd', '--regex-delete', nargs='+', metavar='NAME',
                                                    help=("deletes one/multiple regex by it's name from regex presets. Multiworded"
                                                    " name needs to be quoted. Remove default with 'default'"))
    args = parser.parse_args()

    
    def rename(source, undo=False, quiet=args.quiet, exception_counter=1):
        updated_last_changes = {}

        for original, renamed in source:
            if undo:
                original, renamed = renamed, original   # Swapping values to undo the rename
            try:
                os.rename(original, renamed)
            except FileExistsError:
                renamed = renamed + " ({})".format(exception_counter)
                os.rename(original, renamed)
                exception_counter += 1

            updated_last_changes.update({original: renamed})

            if not quiet:
                print(original, "---->", renamed)
        
        j.json_data['last_changes'] = updated_last_changes
        j.dump()


    if args.path and args.replacewith:
        path = phandler.input_validator(args.path)
        if args.regex:
            regex = args.regex
        elif args.preset_regex:
            try:
                regex = j.json_data['presets'][args.preset_regex]
            except KeyError:
                sys.exit("\nNo preset exists by that name. -rl/--regex-list gives a list of all presets")
        elif j.json_data['regex_default']:
            regex = j.json_data['regex_default']
        else:
            sys.exit(NO_REGEX_MESSAGE)
        
        tobe_renamed = renamed_name(path, args.replacewith, regex, only=args.only, ignore=args.ignore)
        rename(tobe_renamed)
        
    elif args.undo:
        tobe_renamed = j.json_data['last_changes'].items()
        rename(tobe_renamed, undo=True)

    if args.regex_default:
        if isinstance(args.regex_default, str):
            j.json_data['regex_default'] = args.regex_default
            j.dump()
        else:
            print("default: {}".format(j.json_data['regex_default']))

    if args.regex_add:
        if args.regex_add[0] == "default":
            print("Name can't be 'default'")
        else:
            j.append_to_object_element('presets', args.regex_add[0], args.regex_add[1], PRESETS_LIMIT)
            j.dump()

    if args.regex_delete:
        for name in args.regex_delete:
            if name == "default":
                j.json_data['regex_default'] = ""
            else:
                try:
                    del j.json_data['presets'][name]
                except KeyError:
                    print("'{}' is not in presets".format(name))
        j.dump()

    if args.regex_list:
        print("default: {}".format(j.json_data['regex_default']))
        for name, regex in j.json_data['presets'].items():
            print("{}: {}".format(name, regex))