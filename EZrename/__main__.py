import os
import sys
import argparse

import EZrename
from EZrename.confighandler import ConfigHandler
from EZrename.pathhandler import PathHandler

def renaming(parser, args):
    get_ext = lambda en: os.path.splitext(en)[1][1:]

    predicates = []
    if args.directory:
        if args.only:
            predicates.append(lambda e: e.is_dir() or get_ext(e.name) in args.only)
        elif args.ignore:
            predicates.append(lambda e: not e.is_dir() and not get_ext(e.name) in args.ignore)
        else:
            predicates.append(lambda e: e.is_dir())
    else:
        if args.ignore:
            predicates.append(lambda e: not get_ext(e.name) in args.ignore)
        if args.only:
            predicates.append(lambda e: get_ext(e.name) in args.only)

    # config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    # j = ConfigHandler(config_path, limit=5)
    j = args.confighandler
    phandler = PathHandler(invalids=3, sys_exit=True)
    renamer = EZrename.EzRenamer(args.path, phandler)

    if args.undo:
        try:
            source = j.history[renamer.path].items()
        except KeyError:
            parser.error(f"No rename history for this directory.")
    else:
        if args.regex:
            regex = args.regex
        elif args.preset_regex:
            try:
                regex = j.presets[args.preset_regex]
            except KeyError:
                parser.error("No preset exists by that name. -pl/--preset-limit gives a list of all presets.")
        elif j.jsdata['regex_default']:
            regex = j.jsdata['regex_default']
        else:
            parser.error(
                "No default regex is setted up. Use -d/--default <regex pattern> to setup a default pattern. " \
                "Alternatively, use -r/--regex or -pr/--preset-regex."
            )
        filtered = renamer.filter_files(predicates)
        source = renamer.renamed_names(filtered, regex, args.replacewith)

    history = renamer.rename(source, args.undo, args.quiet)
    j.history[renamer.path] = history
    j.dump()

def renamingparser(subparsers):
    """Subparser that deals with renaming."""
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
    j = args.confighandler

    def restrict():
        sys.exit(f"Cannot have more than {j.limit} presets. Remove presets with -pd/--preset-delete <name>.")
    j.on_restriction(restrict)

    if args.default_preset:
        if isinstance(args.default_preset, str):
            j.jsdata['regex_default'] = args.default_preset
            j.dump()
        else:
            print(f"Default: {j.jsdata['regex_default']}")

    elif args.preset_add:
        pres_name, pres_pattern = args.preset_add
        if pres_name == 'default':
            parser.error("Preset name can't be 'default'")
        else:
            j.presupdate({pres_name: pres_pattern})
            j.dump()

    elif args.preset_list:
        default = j.jsdata['regex_default']
        if default:
            print(f"default: {default}")
        for name, pattern in j.presets.items():
            print(f"{name}: {pattern}")

    elif args.preset_delete:
        for name in args.preset_delete:
            if name == 'default':
                j.jsdata['regex_default'] = ""
            else:
                try:
                    del j.presets[name]
                except KeyError:
                    print(f"'{name}' is not in the presets.")
        j.dump()
    
    else:
        parser.error("test")  
            

def configparser(subparsers):
    """Subparser that deals with configuration."""
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
    if args.version:
        print(f"{EZrename.__title__} v{EZrename.__version__}")
    elif args.license:
        print(EZrename.__license__)
    else:
        parser.print_help()

def setparser():
    parser = argparse.ArgumentParser(
        prog=EZrename.__title__, description="Bulk renames files and directories with handy options."
    )
    parser.add_argument('-v', '--version', action='store_true', help="Shows the version.")
    parser.add_argument('-l', '--license', required=False, action='store_true', help="Shows the license.")
    parser.set_defaults(func=parserdefault)

    subparsers = parser.add_subparsers()
    renamingparser(subparsers)
    configparser(subparsers)

    return parser, parser.parse_args()

def main():
    parser, args = setparser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    args.confighandler = ConfigHandler(config_path, limit=5)
    args.func(parser, args)

main()