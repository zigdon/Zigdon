#!/usr/bin/python

import sys
sys.path.append('/home/zigdon/lib/code/eve/evelink')
import evelink
import datetime
import humanize
import re
import evelink.cache.sqlite

from collections import OrderedDict, defaultdict

ITEMS = {
    # P0
    2073: {'tier': 0, 'name': 'Microorganisms', 'type_id': 2073},
    2267: {'tier': 0, 'name': 'Base Metals', 'type_id': 2267},
    2268: {'tier': 0, 'name': 'Aqueous Liquids', 'type_id': 2268},
    2270: {'tier': 0, 'name': 'Noble Metals', 'type_id': 2270},
    2286: {'tier': 0, 'name': 'Planktic Colonies', 'type_id': 2286},
    2288: {'tier': 0, 'name': 'Carbon Compounds', 'type_id': 2288},
    2305: {'tier': 0, 'name': 'Autotrophs', 'type_id': 2305},
    2307: {'tier': 0, 'name': 'Felsic Magma', 'type_id': 2307},
    2308: {'tier': 0, 'name': 'Suspended Plasma', 'type_id': 2308},
    2310: {'tier': 0, 'name': 'Noble Gas', 'type_id': 2310},
    2311: {'tier': 0, 'name': 'Reactive Gas', 'type_id': 2311},
    # P1
    2317: {'tier': 1, 'name': 'Oxides', 'type_id': 2317},
    2389: {'tier': 1, 'name': 'Plasmoids', 'type_id': 2389},
    2392: {'tier': 1, 'name': 'Oxidizing Compound', 'type_id': 2392},
    2393: {'tier': 1, 'name': 'Bacteria', 'type_id': 2393},
    2396: {'tier': 1, 'name': 'Biofuels', 'type_id': 2396},
    2397: {'tier': 1, 'name': 'Industrial Fibers', 'type_id': 2397},
    2398: {'tier': 1, 'name': 'Reactive Metals', 'type_id': 2398},
    2399: {'tier': 1, 'name': 'Precious Metals', 'type_id': 2399},
    3645: {'tier': 1, 'name': 'Water', 'type_id': 3645},
    3683: {'tier': 1, 'name': 'Oxygen', 'type_id': 3683},
    3779: {'tier': 1, 'name': 'Biomass', 'type_id': 3779},
    9828: {'tier': 1, 'name': 'Silicon', 'type_id': 9828},
    # P2
    2312: {'tier': 2, 'name': 'Supertensile Plastics', 'type_id': 2312},
    2327: {'tier': 2, 'name': 'Microfiber Shielding', 'type_id': 2327},
    2329: {'tier': 2, 'name': 'Biocells', 'type_id': 2329},
    2463: {'tier': 2, 'name': 'Nanites', 'type_id': 2463},
    9838: {'tier': 2, 'name': 'Superconductors', 'type_id': 9838},
    # P3
    2348: {'tier': 3, 'name': 'Gel-Matrix Biopaste', 'type_id': 2348},
    17392: {'tier': 3, 'name': 'Data Chips', 'type_id': 17392},
}

SIZES = (0.01, 0.38, 1.5, 6)
for v in ITEMS.values():
    v['size'] = SIZES[v['tier']]

SPACE = {'Launchpad': 10000, 'Storage': 12000}

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

def get_journal_tx():
    journal, _, _ = char.wallet_journal(limit=500)

    def blank_tx():
        return {'timestamp': 0,
                'bounties': 0,
                'duty': 0,
                'sales': 0,
                'purchases': 0}

    types = defaultdict(blank_tx)
    details = []
    for transaction in journal:
        timestamp = datetime.datetime.fromtimestamp(transaction['timestamp'])
        day = timestamp.date()
        if transaction['amount'] >= 0:
            party = transaction['party_1']['name']
        else:
            party = transaction['party_2']['name']
        reason = transaction['reason']
        if party == 'CONCORD' and re.match(r'\d+:\d', reason):
            reason = 'Bounty'
            types[day]['bounties'] += transaction['amount']

        if re.match('(import|export) duty', reason.lower()):
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
        day = timestamp.date()

        if transaction['action'] == 'buy':
            categories[day]['purchases'] += transaction['price'] * transaction['quantity']
        elif transaction['action'] == 'sell':
            categories[day]['sales'] += transaction['price'] * transaction['quantity']

def search_calendar(keyword_list):
    cal_items = char.calendar_events()
    items = []
    for _, event in cal_items[0].iteritems():
        for keyword in keywords:
            if keyword in event['title'].lower():
                start = humanize.naturalday(datetime.datetime.fromtimestamp(event['start_ts']))

                items.append('%s - %s' % (start, event['title']))

    return items

def get_planetary_alerts():
    planets, _, _ = char.planetary_colonies()
    planet_alerts = OrderedDict()

    def get_pin_type(name):
        return name.split()[1]

    def blank_planet():
        return {
            'needs': defaultdict(int),  # id: qty/hr
            'makes': defaultdict(int),  # id: qty/hr
            'has': defaultdict(int),    # id: qty
        }

    def planet_summary(data):
        for section in ('makes', 'has', 'needs'):
            print '  %s:' % section.upper()
            for resource in sorted(data[section],
                                   key=lambda x: (ITEMS[x]['tier'], ITEMS[x]['name'])):
                print '    %-21s %d (%d m3)' % (
                    ITEMS[resource]['name'],
                    data[section][resource],
                    ITEMS[resource]['size'] * data[section][resource])


    planet_state = defaultdict(blank_planet)

    for planet_id, planet_info in planets.items():
        planet_name = '%s: %s' % (
            planet_info['planet']['type_name'],
            planet_info['planet']['name'])

        planet_alerts[planet_name] = []
        routes, _, _ = char.planetary_routes(planet_id)
        route_map = char.planetary_route_map(routes)
        pins, _, _ = char.planetary_pins(planet_id)
        now = datetime.datetime.now()
        for pin in pins.values():
            pin_type = get_pin_type(pin['type']['name'])
            if pin_type == 'Extractor':
                if pin['expiry_ts'] is not None:
                    end = datetime.datetime.fromtimestamp(pin['expiry_ts'])
                    timeleft = end - now
                    if timeleft < datetime.timedelta(1):
                        if timeleft > datetime.timedelta(0):
                            planet_alerts[planet_name].append(
                                'extractor ends in %s' % timeleft)
                        else:
                            planet_alerts[planet_name].append(
                                'extractor ended %s ago' % timeleft)
                else:
                    planet_alerts[planet_name].append('extractor idle!')

            if pin['id'] in route_map:
                delta = 0
                for route_id in route_map[pin['id']]:
                    route = routes[route_id]
                    qty = route['quantity']
                    type_id = route['content']['type']
                    if type_id not in ITEMS:
                        print 'UNKNOWN ITEM: %r' % {
                            'type_id': type_id,
                            'name': route['content']['name']}

                    if pin_type == 'Extractor':
                        planet_state[planet_id]['makes'][type_id] = qty
                    elif route['source_id'] == pin['id']:
                        qty *= -1

                    if pin_type in ('Basic', 'Advanced'):
                        if qty < 0:
                            planet_state[planet_id]['makes'][type_id] -= qty
                        else:
                            planet_state[planet_id]['needs'][type_id] += qty

                # check that we have enough storage for the next day
                if pin_type in ('Launchpad', 'Storage') and delta > 0:
                    total_space = SPACE[pin_type]
                    delta *= 24
                    used_space = sum(
                        [ITEMS[x['type']]['size'] * x['quantity']
                         for x in pin['contents'].values()])

                    if used_space + delta > total_space:
                        waste = used_space + delta - total_space
                        planet_alerts[planet_name].append(
                            'will run out of space: %d m3 wasted.' % waste)



            if pin_type in ('Storage', 'Launchpad'):
                planet_state[planet_id]['has'].update({
                    x['type']: x['quantity'] for x in pin['contents'].values()})

        if False:
            print "\n\nState for %s:\n" % planet_name
            planet_summary(planet_state[planet_id])

        # check that we have what we need for the next day
        for item_id in planet_state[planet_id]['needs']:
            needs = planet_state[planet_id]['needs'][item_id]
            has = planet_state[planet_id]['has'].get(item_id, 0)
            makes = planet_state[planet_id]['makes'].get(item_id, 0)

            delta = (needs - makes)*24.0
            if has < delta:
                planet_alerts[planet_name].append(
                    '%-21s | Have: %7d | Make: %4d | Need: %5d | Short: %4d' % (
                        ITEMS[item_id]['name'], has, makes, needs, has-delta))

    return planet_alerts

FILTER = None
if len(sys.argv) > 1:
    FILTER = sys.argv[1]

for char_id, key_id, vcode, keywords in accounts:
    api = evelink.api.API(api_key=(key_id, vcode),
                          cache=evelink.cache.sqlite.SqliteCache(
                              '/tmp/evecache-wallet.sq3'))
    char = evelink.char.Char(char_id=char_id, api=api)
    sheet, _, _ = char.character_sheet()

    char_name = sheet['name'].upper()

    if FILTER is not None:
        if FILTER.upper() not in char_name:
            print 'Skipping %s.' % char_name
            continue

    print '\n\n==== %s ====' % char_name

    categories, tx_details = get_journal_tx()

    add_market_tx(categories)

    if categories:
        print '\n%10s  %12s  %12s  %12s  %12s' % (
            'Summary', 'Bounties', 'Duty', 'Sales', 'Purchases')
        for date in sorted(categories.keys()):
            cats = categories[date]
            print '%10s: %12s  %12s  %12s  %12s' % (
                humanize.naturalday(date),
                humanize.intcomma(int(cats['bounties'])),
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
        print '\n'

    alerts = get_planetary_alerts()
    for planet, issues in alerts.items():
        if not issues:
            continue
        for issue in issues:
            print '%-28s | %s' % (planet, issue)

    if False:
        print 'Transaction details:\n'
        for entry in tx_details:
            print '{date} | {party:26} | {amount:13,} | {balance:16,} | {reason}'.format(**entry)
