#!misc/bin/python

import datetime
import json
import mechanize
import sys

DEBUG = False

# load yesterday's report by default
date = datetime.date.fromordinal(datetime.date.today().toordinal()-1)
if len(sys.argv) >= 3:
    date = sys.argv[2]

if not DEBUG:
# load creds
    with open(sys.argv[1]) as f:
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
        % date)
    usage = json.loads(br.response().read())
else:
    usage = json.loads(
        '{"data":[0,0,0,0,0,0,0,0,0.2,0.4,0.8,1.6,3.1,3.5,3.3,3,2.4,1.2,0.4,0.1,0,0,0,0,0]}'
    )

def bar(data, peak=100, width=40):
    return '*' * int(1.0 * data / peak * width)

print 'Solar report for %s' % date
print '=' * 47
print ''

peak = max(usage['data'])
for hour in range(24):
    kwh = usage['data'][hour]
    print '%2d %-40s %.1f' % (hour, bar(kwh, peak=peak), kwh)
    hour += 1

print '\nTotal production: %.1f kWh' % sum(usage['data'])

# vim: ts=4 sw=4 sts=4 :
