#!/usr/bin/python

import sys
sys.path.append('/home/zigdon/lib/code/eve/evelink')
import evelink
import datetime
import humanize
import re
import evelink.cache.sqlite

from collections import OrderedDict

accounts = []
with open('/home/zigdon/.everc') as f:
    for line in f:
        char_id, key_id, vcode, keywords = line.split(',', 3)
        char_id = int(char_id)
        key_id = int(key_id)
        vcode = vcode.strip()
        keywords = keywords.lower().strip().split(',')
        accounts.append((char_id, key_id, vcode, keywords))
    f.close()

def default_entry():
    return {'bounties': 0, 'duty': 0, 'sales': 0, 'purchases': 0}

for char_id, key_id, vcode, keywords in accounts:

    api = evelink.api.API(api_key=(key_id, vcode),
                          cache=evelink.cache.sqlite.SqliteCache(
                            '/tmp/evecache-wallet.sq3'))
    char = evelink.char.Char(char_id=char_id, api=api)
    sheet, _, _ = char.character_sheet()
    name = sheet['name'].upper()
    print '==== %s ====' % name

    journal, _, _ = char.wallet_journal(limit=500)
    categories = OrderedDict()
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

    planets, _, _ = char.planetary_colonies()
    alerts = OrderedDict()
    for id, planet in planets.items():
        name = planet['planet']['name']

        alerts[name] = []
        pins, _, _ = char.planetary_pins(id)
        now = datetime.datetime.now()
        for pin in pins.values():
            pintype = pin['type']['name']
            if re.search('Extractor', pintype):
                end = datetime.datetime.fromtimestamp(pin['expiry_ts'])
                timeleft = end - now
                if timeleft < datetime.timedelta(1):
                    alerts[name].append('- extractor ends in %s' % timeleft)

    for planet, issues in alerts.items():
        if not issues:
            continue
        print 'PI issues at %s:' % planet
        for issue in issues:
            print issue

    if False:
        print 'Transaction details:\n'
        print details
