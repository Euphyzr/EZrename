"""
MIT License

Copyright (c) 2020-2021 Euphyzr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import sys
import argparse

if __package__ == '' and not hasattr(sys, 'frozen'):
    # in case of running without -m
    path = os.path.realpath(__file__)
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))
    
import EZrename

def get_predicates(**flags):
    """Returns a list of predicates to be applied for get_file.
    
    kwargs
    ------
    ignore : Sequence
        Ignores file extension in this sequence.
    only : Sequence
        Only accepts file extensions in this sequence.
    directoy : bool
        Calling with ignore, ignores the extensions and directories. If no extension
        is provided then only ignore directories. Calling with only filters only directories
        and those extensions.
    """
    get_ext = lambda filename: os.path.splitext(filename)[1][1:]
    predicates = []

    only = flags.get('only')
    ignore = flags.get('ignore')
    directory = flags.get('directory')

    if directory:
        if only:
            # directory with only includes directories
            predicates.append(lambda e: e.is_dir() or get_ext(e.name) in only)
        elif ignore:
            # directory with ignore ignores directories as well as the given extensions
            predicates.append(lambda e: not e.is_dir() and not get_ext(e.name) in ignore)
        elif not ignore and type(ignore) == list:
            # calling -i without any args gives an empty list use this behaviour to ignore directories only
            predicates.append(lambda e: not e.is_dir())
        else:
            predicates.append(lambda e: e.is_dir())
    else:
        if ignore:
            predicates.append(lambda e: not get_ext(e.name) in ignore)
        if only:
            predicates.append(lambda e: get_ext(e.name) in only)

    return predicates


def renaming(parser, args):
    """The function behind the {rename} subparser."""

    conf = args.confighandler
    phandler = EZrename.utils.PathHandler(invalids=3, sys_exit=True)
    path = phandler.input_validate(args.path)
    predicates = get_predicates(only=args.only, ignore=args.ignore, directory=args.directory)

    if args.undo:
        source = conf.get_history(path)
    else:
        regex = conf.get_regex(regex=args.regex, preset_regex=args.preset_regex)
        source = EZrename.renamed_files(path, EZrename.get_files(path, predicates), regex, args.replacewith)
    if args.quiet:
        on_rename_callback = lambda original, new_name: None
        conf.history[path] = EZrename.rename(source, on_rename=on_rename_callback)
    else:
        conf.history[path] = EZrename.rename(source)

    conf.dump()


def renamingparser(subparsers):
    """The rename subparser setup."""

    parser = subparsers.add_parser('rename', help="bulk renaming.")
    parser.set_defaults(func=renaming)

    parser.add_argument('path', help="Path to target files and directories.")
    parser.add_argument('replacewith', nargs='?', default="",
                        help="Matched pattern are replaced with this." \
                            " Providing none will remove the matched pattern.")

    regexes = parser.add_mutually_exclusive_group()
    regexes.add_argument('-r', '--regex', help="Matches name pattern by this regex.")
    regexes.add_argument('-pr', '--preset-regex', help="Use regex from the presets.")

    parser.add_argument('-i', '--ignore', nargs='*', help="Ignores provided extension(s).")
    parser.add_argument('-o', '--only', nargs='*', help="Only match provided extension(s).")
    parser.add_argument('-d', '--directory', action='store_true',
                        help="Matches directories. If called with -o/--only, matches only extenions and " \
                            "directories. If called with -i/--ignore, then ignores the extensions and directory." \
                            "If all three are called together, the ignore is ignored.")
    
    parser.add_argument('-u', '--undo', action='store_true', help="Undos the previous batch of rename.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Doesn't display the changes.")


def configuring(parser, args):
    """The function behind {config} subparser."""

    conf = args.confighandler
    conf.restriction_msg = f"Cannot have more than {conf.limit} presets. Remove presets with -pd/--preset-delete <name>."

    if args.default_preset:
        # we want to print the current default if no argument was provided
        if isinstance(args.default_preset, str):
            conf.jsdata['regex_default'] = args.default_preset
            conf.dump()
        else:
            print(f"Default: {conf.jsdata['regex_default']}")

    elif args.preset_add:
        pres_name, pres_pattern = args.preset_add
        if pres_name == 'default':
            # we don't want to mixup between the default preset and 
            # the preset named default when deleting the preset
            parser.error("Preset name can't be 'default'")
        else:
            conf.update_preset({pres_name: pres_pattern})
            conf.dump()

    elif args.preset_list:
        default = conf.jsdata['regex_default']
        if default:
            print(f"default: {default}")
        for name, pattern in conf.presets.items():
            print(f"{name}: {pattern}")

    elif args.preset_delete:
        for name in args.preset_delete:
            if name == 'default':
                conf.jsdata['regex_default'] = ""
            else:
                try:
                    del conf.presets[name]
                except KeyError:
                    print(f"'{name}' is not in the presets.")
        conf.dump()


def configparser(subparsers):
    """The config subparser setup."""

    parser = subparsers.add_parser('config', help="Configuring the presets.")
    parser.set_defaults(func=configuring)
    parser.add_argument('-dp', '--default-preset', nargs='?', const=True,
                        help="Setup a default pattern. Providing no argument shows the current default.")
    parser.add_argument('-pl', '--preset-list', action='store_true', help="Shows the current presets.")
    parser.add_argument('-pa', '--preset-add', nargs=2, metavar=('NAME', 'PATTERN'),
                        help="Adds a pattern in the preset. Multi-worded names are to be quoted.")
    parser.add_argument('-pd', '--preset-delete', nargs='+', metavar='NAME',
                        help="Deletes one/multiple presets by it's name. Multi-worded names are to be quoted." \
                            " Remove the default preset by 'default'.")


def parserdefault(parser, args):
    """The function behind default parser."""

    if args.version or args.about:
        print(f"{EZrename.__title__} v{EZrename.__version__}")
    else:
        parser.print_help()


def setparser():
    """The default parser setup."""

    parser = argparse.ArgumentParser(
        prog=EZrename.__title__, description="Bulk renames files and directories with handy options."
    )
    parser.add_argument('-v', '--version', action='store_true', help="Shows the version.")
    parser.add_argument('-a', '--about', required=False, action='store_true', help="About this.")
    parser.set_defaults(func=parserdefault)

    subparsers = parser.add_subparsers()
    renamingparser(subparsers)
    configparser(subparsers)

    return parser, parser.parse_args()


def main():
    parser, args = setparser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    args.confighandler = EZrename.utils.ConfigHandler(config_path, limit=5, errorer=parser.error)
    args.func(parser, args)

if __name__ == "__main__":
    main()