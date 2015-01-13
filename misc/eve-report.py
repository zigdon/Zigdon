#!/usr/bin/python

import sys
sys.path.append('/home/zigdon/lib/code/eve/evelink')
import evelink
import datetime
import humanize
import re
import evelink.cache.shelf

from collections import OrderedDict

with open('/home/zigdon/.everc') as f:
    char_id = int(f.next())
    key_id = int(f.next())
    vcode = f.next().strip()
    keywords = f.next().lower().strip().split(',')
    f.close()

api = evelink.api.API(api_key=(key_id, vcode),
                      cache=evelink.cache.shelf.ShelveCache('/tmp/evecache-wallet'))
char = evelink.char.Char(char_id=char_id, api=api)

journal, _, _ = char.wallet_journal(limit=500)

categories = OrderedDict()
def default_entry():
  return {'bounties': 0, 'duty': 0, 'sales': 0, 'purchases': 0}

details = ''
for entry in journal:
  date = humanize.naturalday(datetime.datetime.fromtimestamp(entry['timestamp']))
  if entry['amount'] >= 0:
    party = entry['party_1']['name']
  else:
    party = entry['party_2']['name']
  reason = entry['reason']
  if party == 'CONCORD' and re.match('\d+:\d', reason):
    reason = 'Bounty'
    if date not in categories:
        categories[date] = default_entry()

    categories[date]['bounties'] += entry['amount']

  if re.match('(import|export) duty', reason.lower()):
    if date not in categories:
        categories[date] = default_entry()
    categories[date]['duty'] += entry['amount']

  details += '%10s | %26s | %13s | %16s | %s\n' % \
    (date, party, humanize.intcomma(entry['amount']),
    humanize.intcomma(entry['balance']), reason)

transactions, _, _ = char.wallet_transactions()
for entry in transactions:
  date = humanize.naturalday(datetime.datetime.fromtimestamp(entry['timestamp']))
  if date not in categories:
    continue

  if entry['action'] == 'buy':
    categories[date]['purchases'] += entry['price'] * entry['quantity']
  elif entry['action'] == 'sell':
    categories[date]['sales'] += entry['price'] * entry['quantity']

print '\n%10s  %12s  %12s  %12s  %12s' % (
    'Summary', 'Bounties', 'Duty', 'Sales', 'Purchases')
for date, cats in categories.iteritems():
    print '%10s: %12s  %12s  %12s  %12s' % (
      date, humanize.intcomma(int(cats['bounties'])),
      humanize.intcomma(int(cats['duty'])),
      humanize.intcomma(int(cats['sales'])),
      humanize.intcomma(int(cats['purchases'])),
      )

print '\nBalance: %s' % humanize.intcomma(int(journal[-1]['balance']))

print '\nUpcoming events of note:'
events = char.calendar_events()
for eid, event in events[0].iteritems():
    for keyword in keywords:
        if keyword in event['title'].lower():
            start = humanize.naturalday(datetime.datetime.fromtimestamp(event['start_ts']))

            print '%s - %s\n' % (start, event['title'])

if False:
    print 'Transaction details:\n'
    print details
