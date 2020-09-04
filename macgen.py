#!/usr/bin/env python3
import os
import sys

import argparse
import secrets

from mac import MAC


def read_OUIs_from_file(filename):
    macs = []
    lines = open(filename).readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[0] == '#':  # skip line that is comment only
            continue

        line_parts = filter(lambda s: s, line.split('\t'))
        line_parts = list(map(lambda s: s.strip(), line_parts))

        if len(line_parts) < 2:
            # we need [mac] and [vendor]
            continue

        line_OUI_part = line_parts[0]
        if line_OUI_part.find('/') > -1:
            # TODO: I don't know how to read this yes.
            continue

        line_vendor_part = line_parts[1]

        if len(line_parts) >= 3:
            line_full_vendor_part = line_parts[2]
            if len(line_parts) >= 4:
                line_comment_part = line_parts[3]
                if len(line_parts) > 4:
                    line = line.replace('\t', '\\t')
                    print(f'Discarding [{" ".join(line_parts[4:])}] '
                          f'from [{line}]')
            else:
                line_comment_part = None
        else:
            line_full_vendor_part = None
            line_comment_part = None

        mac = MAC(line_OUI_part,
                  line_vendor_part,
                  line_full_vendor_part,
                  line_comment_part)

        macs.append(mac)

    return macs

def treat_arg_file(args):
    if not args.file:
        args.file = os.path.dirname(__file__) + os.sep + 'manuf'
    return args

def treat_arg_count(args):
    args.count = args.count % 16777216
    if args.count == 0:
        sys.exit(0)
    return args

def get_argparse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--lucky',
                        help="""
Selects any vendor that matches. If this is not set, you will be prompted to
choose from a list of matched vendors.
""",
                        action='store_true')

    parser.add_argument('-f', '--file',
                        type=str,
                        default=None,
                        help="""
File holding a list of vendors.\t\t
Format: OUI<TAB>vendor<TAB>full vendor info<TAB>comment.\t\t
Full vendor info and comment are
optional. Lines starting with # are ignored.
""")

    parser.add_argument('-s', '--separator',
                        type=str,
                        default=':',
                        help="""
Use the passed separator when printing MAC address. For instance, passing
separator - will print a MAC like XX-YY-ZZ-AA-BB-CC while passing separator as
. will print XX.YY.ZZ.AA.BB.CC. Defaults to :'
""")

    parser.add_argument('-v', '--vendor',
                        type=str,
                        default=None,
                        help="""
%(prog)s will try to generate a MAC address from the vendor passed as argument.
First, it will try to look for a exact match, if no match is found, this
algorithm will be used to try to find a vendor that looks like what you have
typed.
""")

    parser.add_argument('-nl', '--no-levenshtein',
                        action='store_true',
                        help="""
Do not use levenshtein distance when searching for vendors
""")

    parser.add_argument('-pv', '--print-vendor',
                        action='store_true',
                        help='Also prints vendor')

    parser.add_argument('-ll', '--max-levenshtein-distance',
                        type=float,
                        default=3.0,
                        help="""
Sets the maximum levenshtein distance allowed between desired input vendor and
the vendors in input file. Defaults to 3.
""")

    parser.add_argument('-c', '--count',
                        type=int,
                        default=1,
                        help="""
Quantity of MACs to be generated. Truncated to 16.777.215.
""")

    args = parser.parse_args()
    args = treat_arg_file(args)
    args = treat_arg_count(args)

    return args


def read_choice(max_allowed):
    read_choice = False
    while not read_choice:
        try:
            choice = int(input('Which one would you like sir? '))
            if choice < 0 or max_allowed < choice:
                raise
            read_choice = True
        except Exception:
            print(f'Please, sir. Input a choice between 0 and {max_allowed} ')
    return choice


def main():
    args = get_argparse()
    MAC.set_macs(read_OUIs_from_file(args.file))
    MAC.set_levenshtein_max_dist_allowed(args.max_levenshtein_distance)
    if args.vendor is None:
        mac = MAC.get_any()
    else:
        macs = MAC.find_by_vendor(args.vendor, args.no_levenshtein)
        if args.lucky:
            mac = secrets.choice(macs)
        else:
            for i, _mac in enumerate(macs):
                print(f'{str(i).zfill(2)} - {_mac.OUI}: {_mac.vendor}')
            choice = read_choice(i)
            mac = macs[choice]

    for _ in range(args.count):
        output = ''
        if args.print_vendor:
            output += (mac.full_vendor_name or mac.vendor) + ': '
        output += mac.generate_random_mac(args.separator)
        print(output)


if __name__ == '__main__':
    main()
