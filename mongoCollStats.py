#!/usr/bin/env python
#
#
from prettytable import PrettyTable
import psutil
from pymongo import MongoClient
from pymongo import ReadPreference
from optparse import OptionParser

def compute_signature(index):
    signature = index["ns"]
    for key in index["key"]:
        signature += "%s_%s" % (key, index["key"][key])
    return signature

def get_collection_stats(database, collection):
    print "Checking DB: %s" % collection.full_name
    return database.command("collstats", collection.name)

def get_cli_options():
    parser = OptionParser(usage="usage: python %prog [options]",
                          description="""Desc: Show collections status""")

    parser.add_option("-H", "--host",
                      dest="host",
                      default="localhost",
                      metavar="HOST",
                      help="MongoDB host")
    parser.add_option("-p", "--port",
                      dest="port",
                      default=27017,
                      metavar="PORT",
                      help="MongoDB port")
    parser.add_option("-d", "--database",
                      dest="database",
                      default="",
                      metavar="DATABASE",
                      help="database")
    parser.add_option("-u", "--user",
                      dest="user",
                      default="monitor",
                      metavar="USER",
                      help="MongoDB user")
    parser.add_option("--password",
                      dest="password",
                      default="B033562027D95A0F17",
                      metavar="PASSWORD",
                      help="MongoDB password")

    (options, args) = parser.parse_args()

    return options

def get_client(host, port, username, password):
    userPass = ""
    if username and password:
        userPass = username + ":" + password + "@"

    mongoURI = "mongodb://" + userPass + host + ":" + str(port)
    client = MongoClient(mongoURI)
    return client


def convert_bytes(bytes):
    bytes = float(bytes)
    magnitude = abs(bytes)
    if magnitude >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif magnitude >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif magnitude >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif magnitude >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size

def main(options):
    summary_stats = {
        "count" : 0,
        "size" : 0,
        "indexSize" : 0,
        "storageSize" : 0
    }
    all_stats = []

    client = get_client(options.host, options.port,
                        options.user, options.password)
    all_db_stats = {}

    databases= []
    if options.database:
        databases.append(options.database)
    else:
        databases = client.database_names()

    for db in databases:
        # FIXME: Add an option to include oplog stats.
        if db == "local":
            continue

        database = client[db]
        all_db_stats[database.name] = []
        for collection_name in database.collection_names():
            stats = get_collection_stats(database, database[collection_name])
            all_stats.append(stats)
            all_db_stats[database.name].append(stats)

            summary_stats["count"] += stats["count"]
            summary_stats["size"] += stats["size"]
            summary_stats["indexSize"] += stats.get("totalIndexSize", 0)
            summary_stats["storageSize"] += stats.get("storageSize", 0)

    x = PrettyTable(["Collection", "Count", "% Size", "DB Size", "Avg Obj Size", "Indexes", "Index Size", "Storage Size"])
    x.align["Collection"]  = "l"
    x.align["% Size"]  = "r"
    x.align["Count"]  = "r"
    x.align["DB Size"]  = "r"
    x.align["Avg Obj Size"]  = "r"
    x.align["Index Size"]  = "r"
    x.align["Storage Size"]  = "r"
    x.padding_width = 1

    print

    for db in all_db_stats:
        db_stats = all_db_stats[db]
        count = 0
        for stat in db_stats:
            count += stat["count"]
            x.add_row([stat["ns"], stat["count"], "%0.1f%%" % ((stat["size"] / float(summary_stats["size"])) * 100),
                       convert_bytes(stat["size"]),
                       convert_bytes(stat.get("avgObjSize", 0)),
                       stat.get("nindexes", 0),
                       convert_bytes(stat.get("totalIndexSize", 0)),
                       convert_bytes(stat.get("storageSize", 0))
                       ])

    print
    print x.get_string(sortby="% Size")
    print "Total Documents:", summary_stats["count"]
    print "Total Data Size:", convert_bytes(summary_stats["size"])
    print "Total Index Size:", convert_bytes(summary_stats["indexSize"])
    print "Total Storage Size:", convert_bytes(summary_stats["storageSize"])

    # this is only meaningful if we're running the script on localhost
    if options.host == "localhost":
        ram_headroom = psutil.virtual_memory().total - summary_stats["indexSize"]
        print "RAM Headroom:", convert_bytes(ram_headroom)
        print "RAM Used: %s (%s%%)" % (convert_bytes(psutil.virtual_memory().used), psutil.virtual_memory().percent)
        print "Available RAM Headroom:", convert_bytes((100 - psutil.virtual_memory().percent) / 100 * ram_headroom)

if __name__ == "__main__":
    options = get_cli_options()
    main(options)

