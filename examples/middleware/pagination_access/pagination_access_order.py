#!/usr/bin/env python
''' This middleware will check pagination and if an endpoint is being queried in order.
'''


import sys
import re
import logging
from time import sleep
import json


logging.basicConfig(filename='delay_middleware.log', level=logging.DEBUG)
logging.debug('Delay middleware is called')


SLEEP_SECS = 5
LAST_ENDPOINT = None
LAST_PAGE_GROUPING = None
PAGES_ACCESSED = set()


argumentRegEx = re.compile('([\w]+=[\w]+)')
argumentPairRegEx = re.compile('^([\w]+)=([\w]+)$')


def _getArguments(urlQuery):

    arguments = {}
    argumentPairs = argumentRegEx.findall(urlQuery)

    for argumentPair in argumentPairs:

        argumentPairMatch = argumentPairRegEx.match(argumentPair)

        if argumentPairMatch:
            key, value = argumentPairMatch.groups()
            arguments[key] = value

    return arguments


def _parsePagination(urlQuery):

    arguments = _getArguments(urlQuery)

    page = arguments.get('page', '')
    per_page = arguments.get('per_page', '')

    return (int(page) if page.isdigit() else None,
        int(per_page) if per_page.isdigit() else None
    )


def _isPaginationAccessedOrderly(page):

    PAGES_ACCESSED.add(page)
    accessedPageRange = set(xrange(min(PAGES_ACCESSED), max(PAGES_ACCESSED) + 1))

    if sorted(PAGES_ACCESSED)[-1] != page or accessedPageRange.difference(PAGES_ACCESSED):
        return False

    return True


def main(stdin=sys.stdin):

    global LAST_ENDPOINT
    global LAST_PAGE_GROUPING
    global PAGES_ACCESSED

    data = stdin.readlines()
    # this is a json string in one line so we are interested in that one line
    payload = data[0]
    logging.debug("checking pagination access")

    payload_dict = json.loads(payload)

    # Status always ok when middleware is testing.
    payload_dict['response']['status'] = 200

    path = payload_dict['request'].get('path', '')
    query = payload_dict['request'].get('query', '')

    page, per_page = _parsePagination(query)

    # Rest because we track what is accessed in order.
    if LAST_ENDPOINT != path or LAST_PAGE_GROUPING != per_page:
        LAST_ENDPOINT = path
        LAST_PAGE_GROUPING = per_page
        PAGES_ACCESSED = set()

    body = "You called ({}). No pagination. Has query arguments {!r} \n".format(path, _getArguments(query))
    statusTypes = {}

    if not page is None and per_page:

        if page == 0:
            statusTypes['ValidPageIndex'] = 'Invalid page index.'

        statusTypes['pageStatus'] = 'Page not previously accessed.'
        if page in PAGES_ACCESSED:
            statusTypes['pageStatus'] = 'Page accessed.'

        statusTypes['paginationAccessOrderStatus'] = 'Accessed randomly.'
        if _isPaginationAccessedOrderly(page):
            statusTypes['paginationAccessOrderStatus'] = 'Accessed orderly.'

        status = ' '.join([statusTypes[key] for key in sorted(statusTypes.keys())])

        body = "You called ({}). \n" \
           "Pagination requested page {}. \n" \
           "{}\n".format(path, page, status)

    payload_dict['response']['body'] = body

    # do not modifying payload, returning same one
    print(json.dumps(payload_dict))


if __name__ == "__main__":
    main()
