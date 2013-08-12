#!misc/bin/python

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
    br.open('https://oursungevity.com/users/login')

# enter login details
    br.form = list(br.forms())[0]
    br['data[User][email]'] = username
    br['data[User][pass]'] = password

# log in
    resp = br.submit()

# download xls
    br.open(
        'https://oursungevity.com/performance/chart_control/0004A3A18F83/day/%s'
        % args.date)
    usage = json.loads(br.response().read())
else:
    usage = json.loads(
        '{"data":[0,0,0,0,0,0,0,0,0.2,0.4,0.8,1.6,3.1,3.5,3.3,3,2.4,1.2,0.4,0.1,0,0,0,0,0]}'
    )

def bar(data, peak=100, width=40, marker='*'):
    return marker * int(1.0 * data / peak * width)

print 'Solar report for %s' % args.date
print '=' * 47
print ''

peak = max(usage['data'])
for hour in range(24):
    kwh = usage['data'][hour]
    print '%2d %-40s %.1f' % (hour, bar(kwh, peak=peak, marker=args.marker), kwh)
    hour += 1

print '\nTotal production: %.1f kWh' % sum(usage['data'])

# vim: ts=4 sw=4 sts=4 :
