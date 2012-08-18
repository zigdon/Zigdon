#!/usr/bin/python

import sys
sys.path.append("/home/zigdon/lib/code/eve/evelink")
import evelink
import datetime
import humanize
import re
import evelink.cache.shelf ## for testing only

with open("/home/zigdon/.everc") as f:
    char_id = int(f.next())
    key_id = int(f.next())
    vcode = f.next().strip()
    f.close()

api = evelink.api.API(api_key=(key_id, vcode),
                      cache=evelink.cache.shelf.ShelveCache("/tmp/evecache"))
char = evelink.char.Char(char_id=char_id, api=api)

activity = char.wallet_journal()

for entry in activity[-10:]:
  date = humanize.naturalday(datetime.datetime.fromtimestamp(entry['timestamp']))
  if entry['amount'] >= 0:
    party = entry['party_1']['name']
  else:
    party = entry['party_2']['name']
  reason = entry['reason']
  if party == 'CONCORD' and re.match('\d+:\d', reason):
    reason = "Bounty"

  print "%10s | %20s | %12s | %15s | %s" % \
    (date, party, humanize.intcomma(entry['amount']),
    humanize.intcomma(entry['balance']), reason)
