#!/usr/bin/python

import argparse
import datetime
import json
import mechanize
import sys

parser = argparse.ArgumentParser(description='Load solar generation report')
parser.add_argument('--debug', '-n', action='store_true')
parser.add_argument('--marker', default='*')
parser.add_argument('--date')
parser.add_argument('rc')

args = parser.parse_args()

# load yesterday's report by default
if not args.date:
    args.date = datetime.date.fromordinal(datetime.date.today().toordinal()-1)

if not args.debug:
# load creds
    with open(args.rc) as f:
        username = f.next().strip()
        password = f.next().strip()
        f.close()

# create browser
    br = mechanize.Browser()
    br.set_handle_robots(False)

# load login page
    br.open('https://star.oursungevity.com/login')

# enter login details
    br.form = list(br.forms())[0]
    br['email'] = username
    br['password'] = password

# log in
    resp = br.submit()

# download xls
    br.open(
        'https://star.oursungevity.com/api/installation/a1UU0000000JzdRMAS/performance/daily/%s'
        % args.date)
    usage = json.loads(br.response().read())
else:
    usage = json.loads(
        '[{"date":"2013-11-05 00:00:00","kwh":0.0},{"date":"2013-11-05 01:00:00","kwh":0.0},{"date":"2013-11-05 02:00:00","kwh":0.0},{"date":"2013-11-05 03:00:00","kwh":0.0},{"date":"2013-11-05 04:00:00","kwh":0.0},{"date":"2013-11-05 05:00:00","kwh":0.0},{"date":"2013-11-05 06:00:00","kwh":0.0},{"date":"2013-11-05 07:00:00","kwh":0.128},{"date":"2013-11-05 08:00:00","kwh":1.228},{"date":"2013-11-05 09:00:00","kwh":2.062},{"date":"2013-11-05 10:00:00","kwh":2.438},{"date":"2013-11-05 11:00:00","kwh":2.58},{"date":"2013-11-05 12:00:00","kwh":2.531},{"date":"2013-11-05 13:00:00","kwh":2.179},{"date":"2013-11-05 14:00:00","kwh":1.832},{"date":"2013-11-05 15:00:00","kwh":0.948},{"date":"2013-11-05 16:00:00","kwh":0.088},{"date":"2013-11-05 17:00:00","kwh":-0.009},{"date":"2013-11-05 18:00:00","kwh":0.0},{"date":"2013-11-05 19:00:00","kwh":0.0},{"date":"2013-11-05 20:00:00","kwh":0.0},{"date":"2013-11-05 21:00:00","kwh":0.0},{"date":"2013-11-05 22:00:00","kwh":0.0},{"date":"2013-11-05 23:00:00","kwh":0.0}]'
    )

usage = [ x['kwh'] for x in usage ]

def bar(data, peak=100, width=40, marker='*'):
    return marker * int(1.0 * data / peak * width)

print 'Solar report for %s' % args.date
print '=' * 47
print ''

peak = max(usage)
for hour in range(24):
    kwh = usage[hour]
    print '%2d %-40s %.1f' % (hour, bar(kwh, peak=peak, marker=args.marker), kwh)
    hour += 1

print '\nTotal production: %.1f kWh' % sum(usage)

# vim: ts=4 sw=4 sts=4 :
