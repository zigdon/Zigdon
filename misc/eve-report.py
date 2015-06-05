#!/usr/bin/python

import sys
sys.path.append('/home/zigdon/lib/code/eve/evelink')
import evelink
import datetime
import humanize
import re
import evelink.cache.sqlite

from collections import OrderedDict

with open('/home/zigdon/.everc') as f:
    accounts = []
    for line in f:
        char_id, key_id, vcode, keywords = line.split(',', 3)
        char_id = int(char_id)
        key_id = int(key_id)
        vcode = vcode.strip()
        keywords = keywords.lower().strip().split(',')
        accounts.append((char_id, key_id, vcode, keywords))
    f.close()

def default_entry(ts):
    return {'timestamp': ts,
            'bounties': 0,
            'duty': 0,
            'sales': 0,
            'purchases': 0}

def get_journal_tx():
    journal, _, _ = char.wallet_journal(limit=500)
    types = {}
    details = []
    for transaction in journal:
        timestamp = datetime.datetime.fromtimestamp(transaction['timestamp'])
        day = humanize.naturalday(timestamp)
        if transaction['amount'] >= 0:
            party = transaction['party_1']['name']
        else:
            party = transaction['party_2']['name']
        reason = transaction['reason']
        if party == 'CONCORD' and re.match(r'\d+:\d', reason):
            reason = 'Bounty'
            if day not in types:
                types[day] = default_entry(timestamp)

            types[day]['bounties'] += transaction['amount']

        if re.match('(import|export) duty', reason.lower()):
            if day not in types:
                types[day] = default_entry(timestamp)
            types[day]['duty'] += transaction['amount']

        details.append({'date': day,
                        'party': party,
                        'amount': transaction['amount'],
                        'balance': transaction['balance'],
                        'reason': reason})


    return types, details

def add_market_tx(categories):
    transactions, _, _ = char.wallet_transactions()
    for transaction in transactions:
        timestamp = datetime.datetime.fromtimestamp(transaction['timestamp'])
        day = humanize.naturalday(timestamp)
        if day not in categories:
            categories[day] = default_entry(timestamp)

        if transaction['action'] == 'buy':
            categories[day]['purchases'] += transaction['price'] * transaction['quantity']
        elif transaction['action'] == 'sell':
            categories[day]['sales'] += transaction['price'] * transaction['quantity']

    return categories

def search_calendar(keyword_list):
    cal_items = char.calendar_events()
    items = []
    for _, event in cal_items[0].iteritems():
        for keyword in keywords:
            if keyword in event['title'].lower():
                start = humanize.naturalday(datetime.datetime.fromtimestamp(event['start_ts']))

                items.append('%s - %s' % (start, event['title']))

    return items

for char_id, key_id, vcode, keywords in accounts:

    api = evelink.api.API(api_key=(key_id, vcode),
                          cache=evelink.cache.sqlite.SqliteCache(
                              '/tmp/evecache-wallet.sq3'))
    char = evelink.char.Char(char_id=char_id, api=api)
    sheet, _, _ = char.character_sheet()
    name = sheet['name'].upper()
    print '\n\n==== %s ====' % name

    categories, tx_details = get_journal_tx()

    categories = add_market_tx(categories)

    if categories:
        print '\n%10s  %12s  %12s  %12s  %12s' % (
            'Summary', 'Bounties', 'Duty', 'Sales', 'Purchases')
        for date in sorted(categories.keys(),
                           key=lambda x: categories[x]['timestamp']):
            cats = categories[date]
            print '%10s: %12s  %12s  %12s  %12s' % (
                date, humanize.intcomma(int(cats['bounties'])),
                humanize.intcomma(int(cats['duty'])),
                humanize.intcomma(int(cats['sales'])),
                humanize.intcomma(int(cats['purchases'])),
            )

    info, _, _ = char.wallet_info()
    print '\nBalance: %s' % humanize.intcomma(info['balance'])


    events = []
    if keywords:
        events.extend(search_calendar(keywords))

    if events:
        print '\nUpcoming events of note:'
        print '\n'.join(['  %s' % e for e in events])

    planets, _, _ = char.planetary_colonies()
    alerts = OrderedDict()
    for planet_id, planet in planets.items():
        name = planet['planet']['name']

        alerts[name] = []
        pins, _, _ = char.planetary_pins(planet_id)
        now = datetime.datetime.now()
        for pin in pins.values():
            pintype = pin['type']['name']
            if re.search('Extractor', pintype):
                if pin['expiry_ts'] is not None:
                    end = datetime.datetime.fromtimestamp(pin['expiry_ts'])
                    timeleft = end - now
                    if timeleft < datetime.timedelta(1):
                        if timeleft > datetime.timedelta(0):
                            alerts[name].append('- extractor ends in %s' % timeleft)
                        else:
                            alerts[name].append('- extractor ended %s ago' % timeleft)
                else:
                    alerts[name].append('* extractor idle!')

    for planet, issues in alerts.items():
        if not issues:
            continue
        print 'PI issues at %s:' % planet
        for issue in issues:
            print issue

    if False:
        print 'Transaction details:\n'
        for entry in tx_details:
            print '{date} | {party:26} | {amount:13,} | {balance:16,} | {reason}'.format(**entry)

