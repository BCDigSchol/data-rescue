#!/usr/bin/env python
"""Fetch indivdual IMLS resources gathered from data.gov 

This script looks for imls-gov.json within a relative data/imls/ file path.
It will parse through the json file and fetch all the listed resource files.
It then creates sub directories for each fetched resource.

Note: Code has been tested with Python 2.7.13 and untested with Python 3.x
"""

import json
import os
import errno
import re
import urllib2
import sys
import time


__author__ = "Jesse Martinez"

__maintainer__ = "Jesse Martinez"
__email__ = "jesse.martinez@bc.edu"
__status__ = "Works but use at your own risk!"

# time in seconds between getting another resource
cooldown_time = 1

# file paths
file_parent_path = "data/"
file_sub_path = "imls/"
file_path = file_parent_path + file_sub_path
file_name = "imls-gov.json"
file_location = file_path + file_name

result_harvest_url_prefix = "https://catalog.data.gov/harvest/object/"

def printOut(outfile, str):
    """utility function to print to standard out and to file"""
    print str
    if outfile:
        outfile.write("\n" + str)

def getResource(url, file_path_and_name):
    """grabs the resource and save it to local file """
    if not url or not file_path_and_name:
        return None

    #printOut(file_log, "URL: %s" % url)
    #printOut(file_log, "file_path_and_name: %s" % file_path_and_name)

    # http://stackoverflow.com/questions/1726402/in-python-how-do-i-use-urllib-to-see-if-a-website-is-404-or-200
    # TODO: use urllib.urlencode to make sure urls are encoded
    req = urllib2.Request(url)
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        if e.code == 404:
            printOut(file_log, "Received 404. Could not fild file!")
        else:
            printOut(file_log, "Received %s. Could not fild file!" % e.code)
        return None
    except urllib2.URLError as e:
        printOut(file_log, "Could not find file! Error message: %s" % e)
        return None
    else:
        # Received 200
        body = resp.read()
    try:
        with open(file_path_and_name, "wb") as local_file:
            local_file.write(body)
        local_file.close()
        file_size = os.path.getsize(file_path_and_name)

        # we assume the file size is greater than 0
        return file_size
    except EnvironmentError:
        printOut(file_log, "Error: Can't save file: %s" % file_path_and_name)

    return None

def fetch():
    """main method to fetch resources"""
    # create log file
    file_time = time.strftime("%Y%m%d-%H%M%S")
    #file_log_name = "log-%s.txt" % file_time
    file_log_name = "log.txt"
    try:
        file_log = open(file_path + file_log_name, "w")
        printOut(file_log, "Script started at %s" % file_time)
        printOut(file_log, "\nCooldown time between calls %s" % cooldown_time)

    except IOError:
        printOut(None, "Error: Could not write to file: %s%s" % (file_path, file_log_name) )
        printOut(None, "Exiting script\n")
        sys.exit()

    # read in json file
    try:
        with open(file_location) as data_file:
            data = json.load(data_file)
        printOut(file_log, "Read in file: %s" % file_location)
    except EnvironmentError:
        printOut(file_log, "Error: Can't open file: %s" % file_location)
        printOut(file_log, "Exiting script")
        file_log.close()
        sys.exit()

    # loop through and grab each resource from each result
    for res in data["result"]["results"]:
        res_title = res["title"]
        res_title_clean = re.sub('[^0-9a-zA-Z]+', '_', res_title)
        res_name = res["name"]
        res_dir = file_path + res_name + "/"

        printOut(file_log, "\nFound result title: %s" % res_title)

        # create directory for this result
        # on fail, write to parent directory
        # TODO: check if parent directory is writable
        if not os.path.exists(res_dir):
            try:
                os.makedirs(res_dir)
                printOut(file_log, "Created directory: %s" % res_dir)
            except OSError:
                printOut(file_log, "Error: Can't create directory: %s" % res_dir)
                # at this point we'll try to write to the parent directory
                res_dir = file_path
                printOut(file_log, "Warning: Writing to parent directory instead: %s" % res_dir)
        else:
            printOut(file_log, "Found existing directory: %s" % res_dir)

        # check that there is an "extras" section in json file
        # exit if not found
        if "extras" not in res:
            printOut(file_log, "Could not find expected results in json file! Missing 'extras' section. Exiting")
            sys.exit()

        # get harvest_object_id file
        # save as data.json
        found_harvest_object_id = False
        for extra in res["extras"]:
            if "key" in extra and extra["key"] == "harvest_object_id" and not found_harvest_object_id:
                harvest_object_id_url = result_harvest_url_prefix + extra["value"]
                #print result_harvest_url + extra["value"]
                found_harvest_object_id = True

                download_status = "Downloading data.json ... "

                # get the resource
                # returns file size on success and None on failure
                resp = getResource(result_harvest_url_prefix + extra["value"], res_dir + "/data.json")

                if resp:
                    printOut(file_log, download_status + "success! file size %s bytes" % resp)
                else:
                    # this failed but we continue to the next resource
                    printOut(file_log, download_status + "failed. See log file for description")

        # check that there is an "extras" section in json file
        # exit if not found
        if "resources" not in res and "resource" not in res["resources"]:
            printOut(file_log, "Could not find exprected results in json file! Missing 'resources' section. Exiting")
            sys.exit()

        # get each resource
        for resource in res["resources"]:
            resource_url = resource.get("url")
            resource_format = resource.get("format")
            resource_description = resource.get("description")

            # when in doubt, give it a txt extension
            if not resource_format:
                resource_format = ".txt"
            else:
                resource_format = "." + resource_format.lower()

            if not resource_url:
                printOut(file_log, "Could not find url for resource!")
                continue

            # check to see if there is a resource_description
            if resource_description:
                file_name_and_path = res_dir + resource_description
            else:
                file_name_and_path = res_dir + res_name + resource_format

            download_status = "Downloading %s as %s ... " % (resource["url"], file_name_and_path)
                
            # get the resource
            # returns file size on success and None on failure
            time.sleep(cooldown_time)
            resp = getResource(resource["url"], file_name_and_path)
            #resp = None

            if resp:
                printOut(file_log, download_status + "success! File size %s bytes" % resp)
            else:
                # this failed but we continue to the next resource
                printOut(file_log, download_status + "failed. See log file for description")

    file_time = time.strftime("%Y%m%d-%H%M%S")
    printOut(file_log, "\nScript ended at %s" % file_time)

    file_log.close()

if __name__ == "__main__":
    fetch()