#!/usr/bin/python

import sys
sys.path.append("/home/zigdon/lib/code/eve/evelink")
import evelink
import datetime
import humanize
import re
import evelink.cache.shelf

from collections import defaultdict

with open("/home/zigdon/.everc") as f:
    char_id = int(f.next())
    key_id = int(f.next())
    vcode = f.next().strip()
    keywords = f.next().lower().strip().split(',')
    f.close()

api = evelink.api.API(api_key=(key_id, vcode),
                      cache=evelink.cache.shelf.ShelveCache("/tmp/evecache-wallet"))
char = evelink.char.Char(char_id=char_id, api=api)

activity = char.wallet_journal()

bounties = defaultdict(int)

for entry in activity:
  date = humanize.naturalday(datetime.datetime.fromtimestamp(entry['timestamp']))
  if entry['amount'] >= 0:
    party = entry['party_1']['name']
  else:
    party = entry['party_2']['name']
  reason = entry['reason']
  if party == 'CONCORD' and re.match('\d+:\d', reason):
    reason = "Bounty"
    bounties[date] += entry['amount']

  print "%10s | %26s | %12s | %16s | %s" % \
    (date, party, humanize.intcomma(entry['amount']),
    humanize.intcomma(entry['balance']), reason)

print "\nBounties:"
for date, value in bounties.iteritems():
    print "%10s: %s" % (date, humanize.intcomma(value))

print "\nUpcoming events of note:"
events = char.calendar_events()
for eid, event in events.iteritems():
    for keyword in keywords:
        if keyword in event['title'].lower():
            start = humanize.naturalday(datetime.datetime.fromtimestamp(event['start_ts']))

            print "%s - %s\n" % (start, event['title'])
