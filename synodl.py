#!/usr/bin/env python

import logging
import sys
from getpass import getpass
from optparse import OptionParser
from synology.downloadstation import DownloadStation

logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)

command = ""

def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def human_sizeof(num):
    for x in ['B', 'KB', 'MB', 'GB']:
        if(num < 1024.0):
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def usage():
    print(
        "Usage: %s <help|add|list> [options]" % sys.argv[0],
        "Global options:",
        " -u, --user        Username of the account to use for authentication",
        "                   Defaults to 'admin'",
        " -p, --password    Password of the account to use for authentication",
        "                   Asked if not provided",
        " -H, --host        Hostname or IP address of the Synology",
        "                   Defaults to 'syno'",
        " -P, --port        Port to connect to the Synology",
        "                   Defaults to 5000",
        " -s, --secure      Use https to connect the Synology",
        " -h, --help        Show this help",
        " -v, --verbose     Increases verbosity (cumulative)",
        "",
        "Commands options:",
        " add [-d destination] URL",
        "   Adds the specified URL to download queue, destination on the synology",
        "   can be specified",
        "",
        " list",
        "   Lists the current downloads, finished or in progress",
        "",
        " help",
        "   Shows this help",
        sep="\n"
    )


def parse_command_line():
    if len(sys.argv) < 2:
        print_error("Missing parameters.")
        usage()
        sys.exit(1)

    command = sys.argv.pop(1)
    parser = get_global_options_parser()

    if command == "add":
        parse_add_command(parser)
        command_func = add_downloads
    elif command == "list":
        parse_list_command(parser)
        command_func = list_downloads
    elif command in ["-h", "--help", "h", "help"]:
        usage()
        sys.exit(0)
    else:
        print_error("Unknown '%s' command" % command)
        usage()
        sys.exit(1)

    (options, args) = parser.parse_args()
    return (command_func, options, args)


def get_global_options_parser():
    parser = OptionParser(add_help_option=False)
    parser.add_option(
        "-v", "--verbose",
        dest="verbosity",
        action="count"
    )
    parser.add_option(
        "-h", "--help",
        dest="help",
        action="store_true",
        default=False
    )

    parser.add_option(
        "-u", "--user",
        dest="user",
        default="admin"
    )
    parser.add_option(
        "-p", "--password",
        dest="password"
    )

    parser.add_option(
        "-H", "--host",
        dest="host",
        default="syno"
    )
    parser.add_option(
        "-P", "--port",
        dest="port",
        default=5000
    )

    parser.add_option(
        "-s", "--secure",
        dest="secure",
        default=False,
        action="store_true"
    )

    return parser


def parse_add_command(parser):
    # Actions
    parser.add_option(
        "-d", "--destination",
        help="Sets the download destination, e.g. video/Films",
        dest="destination"
    )


def parse_list_command(parser):
    pass


def add_downloads(ds, options, args):
    for url in args:
        logging.info("Adding download %s" % url)
        ds.add(url, destination=options.destination)


def list_downloads(ds, options, args):
    dl_list = ds.list()
    fields_max_length = [0, 0, 0, 0, 0]
    titles = [
        "Download",
        "Destination",
        "Status",
        "Downloaded",
        "Total"
    ]

    for dl in dl_list:
        fields_max_length = [
            max(len(dl['title']), len(titles[0]), fields_max_length[0]),
            max(len(dl['additional']['detail']['destination']), len(titles[1]), fields_max_length[1]),
            max(len(dl['status']), len(titles[2]), fields_max_length[2]),
            max(len(human_sizeof(dl['additional']['transfer']['size_downloaded'])), len(titles[3]), fields_max_length[3]),
            max(len(human_sizeof(dl['size'])), len(titles[4]), fields_max_length[4])
        ]
    format_string = "%%-%ds  %%-%ds  %%-%ds  %%%ds / %%-%ds" % tuple(fields_max_length)

    print(format_string % tuple(titles))

    for dl in dl_list:
        print(
            format_string
            % (
                dl['title'],
                dl['additional']['detail']['destination'],
                dl['status'],
                human_sizeof(dl['additional']['transfer']['size_downloaded']),
                human_sizeof(dl['size'])
            )
        )

def main():
    (command_func, options, args) = parse_command_line()

    if options.help:
        usage()
        sys.exit(0)

    if not options.password:
        options.password = getpass(prompt="%s@%s's password: " % (options.user, options.host))

    if options.verbosity:
        if options.verbosity == 1:
            logging.getLogger().setLevel(logging.INFO)
        if options.verbosity == 2:
            logging.getLogger().setLevel(logging.DEBUG)
        if options.verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.INFO)
            requests_log.propagate = True

    ds = DownloadStation(
        options.host,
        options.user,
        options.password,
        port=options.port,
        use_https=options.secure
    )
    command_func(ds, options, args)

if __name__ == "__main__":
    main()
