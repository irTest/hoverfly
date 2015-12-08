#!/usr/bin/env python

import requests
from argparse import ArgumentParser
import pickle
 
limit = 50

def pagination_links():

    link = "http://readthedocs.org/api/v1/project/?limit=%s&amp;offset=0" % limit
    response = requests.get(link)
    print("url: %s, status code: %s" % (link, response.status_code))
 
 
# main function
def main():
    parser = ArgumentParser(description="Perform proxy testing/URL list creation from pagination")
    args = parser.parse_args()
 
    pagination_links()
 
 
if __name__ == "__main__":
    main()

