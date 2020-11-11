import os
import sys
import argparse

import EZrename
from EZrename.confighandler import ConfigHandler
from EZrename.pathhandler import PathHandler

def setparser():
    parser = argparse.ArgumentParser(description="Bulk renames files and directories with handy options.")
    parser.add_argument('-v', '--version', action='store_true', help="Shows the version.")
    parser.add_argument('-s', '--source', action='store_true', help="Shows the license.")
    subparsers = parser.add_subparsers()
    return parser, subparsers

def renamingparser(subparsers):
    """Subparser that deals with renaming."""
    renaming = subparsers.add_parser('rename', help="bulk renaming.")
    renaming.add_argument('path', help="Path to target files and directories.")
    renaming.add_argument('replacewith', nargs='?', default="",
                        help="Matched pattern are replaced with this." \
                            " Providing none will remove the matched pattern.")

    regexes = renaming.add_mutually_exclusive_group()
    regexes.add_argument('-r', '--regex', help="Matches name patten by this regex.")
    regexes.add_argument('-pr', '--preset-regex', help="Use regex from the presets.")

    renaming.add_argument('-i', '--ignore', nargs='*', help="Ignores provided extension(s).")
    renaming.add_argument('-o', '--only', nargs='*', help="Only match provided extension(s).")
    renaming.add_argument('-d', '--directory', action='store_true',
                        help="Matches directories. If called with -o/--only, matches only extenions and " \
                            "directories. If called with -i/--ignore, then ignores the extensions and directory." \
                            "If all three are called together, the ignore is ignored.")
    
    renaming.add_argument('-u', '--undo', action='store_true', help="Undos the previous batch of rename.")
    renaming.add_argument('-q', '--quiet', action='store_true', help="Doesn't display the changes.")

def renaming(args):
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

    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    j = ConfigHandler(config_path, limit=5)
    phandler = PathHandler(invalids=3, sys_exit=True)
    renamer = EZrename.EzRenamer(args.path, phandler)

    @j.on_restriction
    def cancel_on_restriction():
        sys.exit(f"Cannot have more than {j.limit} presets.")

    if args.undo:
        try:
            source = j.history[renamer.path].items()
        except KeyError:
            sys.exit(f"No rename history for this directory.")
    else:
        if args.regex:
            regex = args.regex
        elif args.preset_regex:
            try:
                regex = j.presets[args.preset_regex]
            except KeyError:
                sys.exit("No preset exists by that name. -pl/--preset-limit gives a list of all presets.")
        elif j.redefault:
            regex = j.redefault
        else:
            sys.exit(
                "No default regex is setted up. Use -d/--default <regex pattern> to setup a default pattern. " \
                "Alternatively, use -r/--regex or -pr/--preset-regex."
            )
        filtered = renamer.filter_files(predicates)
        source = renamer.renamed_names(filtered, regex, args.replacewith)

    history = renamer.rename(source, args.undo, args.quiet)
    j.history[renamer.path] = history
    j.dump()

def configparser(subparsers):
    """Subparser that deals with configuration."""
    configing = subparsers.add_parser('config', help="Configuring the presets.")
    configing.add_argument('-d', '--default', nargs='?', const=True,
                        help="Setup a default pattern. Providing no argument shows the current default.")
    configing.add_argument('-pl', '--preset-list', action='store_true', help="Shows the current presets.")
    configing.add_argument('-pa', '--preset-add', nargs=2, metavar=('NAME', 'PATTERN'),
                        help="Adds a pattern in the preset. Multi-worded names are to be quoted.")
    configing.add_argument('-pd', '--preset-delete', nargs='+', metavar='NAME',
                        help="Deletes one/multiple presets by it's name. Multi-worded names are to be quoted." \
                            " Remove the default preset by 'default'.")

def main():
    parser, subparsers = setparser()
    renamingparser(subparsers)
    args = parser.parse_args()
    renaming(args)

main()