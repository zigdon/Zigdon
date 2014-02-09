#!/usr/bin/python

""" Monitor spoonrocket item availability. Will loop over the site's data feed
until it finds the item is not sold out. Will exit with a status of 0 on
success, 1 if there was an error. """

import sys
import httplib2
import json
import time

from optparse import OptionParser

parser = OptionParser()

parser.add_option("-s", "--sleep", dest="sleep", default=5,
                  help="Seconds to wait between polls")
parser.add_option("-u", "--url", dest="url",
                  default="http://api.spoonrocket.com/userapi//menu?zone_id=8",
                  help="Spoonrocket URL to poll")
parser.add_option("-v", "--vegetarian", action="store_true",
                  dest="vegetarian", default=True)
parser.add_option("-m", "--meat", action="store_false", dest="vegetarian")

(options, args) = parser.parse_args()

h = httplib2.Http(disable_ssl_certificate_validation=True)
while True:
    resp, data = h.request(options.url)

    if resp['status'] != '200':
        print "Failed to poll spoonrocket, request returned:\n%r" % resp
        sys.exit(1)

    try:
        j = json.loads(data)
    except ValueError, e:
        print "Failed to parse json: %s" % E
        sys.exit(1)

    info = None
    for i in j['menu']:
        if options.vegetarian and i['properties'].find('vegetarian') > -1:
            info = i
            break
        if not options.vegetarian and i['properties'].find('vegetarian') == -1:
            info = i
            break

    status = info['sold_out_temporarily'] and 'sold out' or str(info['qty'])
    print "%s: %s" % (info['name'], status)

    if status != 'sold out':
        sys.exit(0)

    time.sleep(options.sleep)


"""
GET https://api.spoonrocket.com/userapi//menu?zone_id=8 | python -c "
import json, sys
j = json.loads(sys.stdin.read())
for i in j['menu']:
      if i['properties'].find('vegetarian') > -1:
            print i['sold_out_temporarily'] and 'sold out' or i['qty']"
"""
