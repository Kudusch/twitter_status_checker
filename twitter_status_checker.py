#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import requests
import json
from datetime import datetime
from urllib.parse import urlparse
from urllib.parse import parse_qs
import glob
import ast
import multiprocessing as mp

base_path = "./"

def checkStatus(tweet):
    n = tweet[0]
    status_id = tweet[1]
    u = tweet[2]

    try:
        r = requests.get(u)
        execution_time = datetime.now().timestamp()
        return_time = str(r.elapsed.total_seconds())
        if r.status_code == 200:
            if(
                len(r.history) > 0 and 
                r.history[0].status_code == 302 and 
                r.url == "https://twitter.com/account/suspended"
                ):
                return_value = "suspended"
            else:
                if ("protected_redirect" in parse_qs(urlparse(r.url).query).keys()):
                    return_value = "protected"
                else:
                    return_value = "online"
        elif r.status_code == 404:
            return_value = "deleted"
        else:
            return_value = str(r.status_code)
    except Exception as e:
        return_value = "error"
        return_time = "NA"
        execution_time = datetime.now().timestamp()
        
    return([status_id, return_value, execution_time])

# tweet_list must be a dictonary, containing tweet urls as values and tweet status ids as keys
tweet_list = {…}

now = datetime.now()

cpu_count = (mp.cpu_count() * 2) - 1
p = mp.Pool(cpu_count)
status_list = p.map(checkStatus, [(n, status_id, url) for n, (status_id, url) in enumerate(tweet_list.items())])
p.close()

n_tweets = len(status_list)

out_file = now.strftime(base_path + "status_%s.csv")
with open(out_file, 'w') as out_file:
    writer = csv.writer(out_file, delimiter=";")
    writer.writerow(["status_id", "status", "ts"])
    for row in status_list:
        writer.writerow(row)

print(datetime.today().strftime("%Y-%m-%d %H:%M:%S") + " | Checked {} tweets in {} ({} seconds).".format(n_tweets, str((datetime.now() - now))[:-7],  int((datetime.now() - now).total_seconds())))