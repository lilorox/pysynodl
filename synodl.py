#!/usr/bin/env python

import configparser
import logging
import os.path
import sys
from getpass import getpass
from optparse import OptionParser
from synology.downloadstation import DownloadStation

logging.basicConfig(
    format="%(asctime)-15s %(levelname)-6s %(name)-8s %(message)s",
    level=logging.ERROR
)

command = ""
config_file = os.path.join(os.path.expanduser("~"), ".synodl.ini")

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
        "Configuration file:",
        " The script will look for the file ~/.synodl.ini to load the default values",
        " that can be overriden by the following options.",
        "",
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
        " add [-d dest|--destination=dest] URL",
        "   Adds the specified URL to download queue, destination on the synology",
        "   can be specified",
        "",
        " list",
        "   Lists the current downloads, finished or in progress",
        "",
        " delete [-f|--force] [-a|--all] id1 id2 id3",
        "   Removes the downloads specified by their ids.",
        "   If -f / --force is used, it will also remove unfinished downloads.",
        "   If -a / --all is used, it will remove all downloads.",
        "",
        " help",
        "   Shows this help",
        sep="\n"
    )


def parse_command_line(config):
    if len(sys.argv) < 2:
        print_error("Missing parameters.")
        usage()
        sys.exit(1)

    command = sys.argv.pop(1)
    parser = get_global_options_parser(config)

    if command == "add":
        parse_add_command(parser)
        command_func = add_downloads
    elif command == "list":
        parse_list_command(parser)
        command_func = list_downloads
    elif command == "delete":
        parse_delete_command(parser)
        command_func = delete_downloads
    elif command in ["-h", "--help", "h", "help"]:
        usage()
        sys.exit(0)
    else:
        print_error("Unknown '%s' command" % command)
        usage()
        sys.exit(1)

    (options, args) = parser.parse_args()
    return (command_func, options, args)


def parse_config():
    if not os.path.isfile(config_file):
        return {}

    config = configparser.ConfigParser()
    config.read(config_file)
    if "synology" not in config.sections():
        return {}

    conf = config['synology']
    if "secure" in conf:
        if conf['secure'] == "true" or conf['secure'] == "yes":
            conf['secure'] = "true"
        else:
            conf['secure'] = "false"

    return conf


def get_global_options_parser(config):
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
        default=config["user"] if "user" in config else "admin"
    )
    parser.add_option(
        "-p", "--password",
        dest="password",
        default=config["password"] if "password" in config else "syno"
    )

    parser.add_option(
        "-H", "--host",
        dest="host",
        default=config["host"] if "host" in config else "syno"
    )
    parser.add_option(
        "-P", "--port",
        dest="port",
        default=config["port"] if "port" in config else 5000
    )

    parser.add_option(
        "-s", "--secure",
        dest="secure",
        action="store_true",
        default=config["secure"] if "secure" in config else False
    )

    return parser


def parse_add_command(parser):
    parser.add_option(
        "-d", "--destination",
        dest="destination"
    )


def parse_list_command(parser):
    pass


def parse_delete_command(parser):
    parser.add_option(
        "-f", "--force",
        dest="force",
        default=False,
        action="store_true"
    )

    parser.add_option(
        "-a", "--all",
        dest="all",
        default=False,
        action="store_true"
    )


def add_downloads(ds, options, args):
    for url in args:
        logging.info("Adding download %s" % url)
        ds.add(url, destination=options.destination)


def list_downloads(ds, options, args):
    dl_list = ds.list()
    fields_max_length = [0, 0, 0, 0, 0, 0]
    titles = [
        "Id",
        "Download",
        "Destination",
        "Status",
        "Downloaded",
        "Total"
    ]

    for dl in dl_list:
        fields_max_length = [
            max(len(dl['id']), len(titles[0]), fields_max_length[0]),
            max(len(dl['title']), len(titles[1]), fields_max_length[1]),
            max(len(dl['additional']['detail']['destination']), len(titles[2]), fields_max_length[2]),
            max(len(dl['status']), len(titles[3]), fields_max_length[3]),
            max(len(human_sizeof(float(dl['additional']['transfer']['size_downloaded']))), len(titles[4]), fields_max_length[4]),
            max(len(human_sizeof(float(dl['size']))), len(titles[5]), fields_max_length[5])
        ]
    format_string = "%%-%ds %%-%ds  %%-%ds  %%-%ds  %%%ds / %%-%ds" % tuple(fields_max_length)

    print(format_string % tuple(titles))
    for dl in dl_list:
        print(
            format_string
            % (
                dl['id'],
                dl['title'],
                dl['additional']['detail']['destination'],
                dl['status'],
                human_sizeof(float(dl['additional']['transfer']['size_downloaded'])),
                human_sizeof(float(dl['size']))
            )
        )


def delete_downloads(ds, options, id_list):
    if options.all:
        id_list = [dl['id'] for dl in ds.list()]
    logging.info("Deleting downloads %s" % ",".join(id_list))
    ds.delete(id_list, force=options.force)


def main():
    config = parse_config()
    (command_func, options, args) = parse_command_line(config)

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
    options.secure="True"
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
