#!/usr/bin/python

import sys
import datetime
import gflags
import humanize
import operator
import os
import re
import time

sys.path.append('/home/zigdon/lib/code/eve/evelink')
import evelink
import evelink.cache.sqlite

from collections import OrderedDict, defaultdict
from pprint import pprint

FLAGS = gflags.FLAGS

gflags.DEFINE_string('debug_char', None, 'Character substring to debug.')
gflags.DEFINE_string('debug_planet', None, 'Planet substring to debug.')
gflags.DEFINE_boolean('show_state', False, 'Display planet state.')
gflags.DEFINE_boolean('debug', False, 'Display internal deubgging info.')
gflags.DEFINE_boolean('transaction_details', False, 'Show full transaction log.')
gflags.DEFINE_string('export_tx', None, 'Export transaction data to named file.')

ITEMS = {
    # P0
    2073: {'tier': 0, 'name': 'Microorganisms', 'type_id': 2073, 'req': []},
    2267: {'tier': 0, 'name': 'Base Metals', 'type_id': 2267, 'req': []},
    2268: {'tier': 0, 'name': 'Aqueous Liquids', 'type_id': 2268, 'req': []},
    2270: {'tier': 0, 'name': 'Noble Metals', 'type_id': 2270, 'req': []},
    2272: {'tier': 0, 'name': 'Heavy Metals', 'type_id': 2272, 'req': []},
    2286: {'tier': 0, 'name': 'Planktic Colonies', 'type_id': 2286, 'req': []},
    2288: {'tier': 0, 'name': 'Carbon Compounds', 'type_id': 2288, 'req': []},
    2305: {'tier': 0, 'name': 'Autotrophs', 'type_id': 2305, 'req': []},
    2306: {'tier': 0, 'name': 'Non-CS Crystals', 'type_id': 2306, 'req': []},
    2307: {'tier': 0, 'name': 'Felsic Magma', 'type_id': 2307, 'req': []},
    2308: {'tier': 0, 'name': 'Suspended Plasma', 'type_id': 2308, 'req': []},
    2309: {'tier': 0, 'name': 'Ionic Solutions', 'type_id': 2309, 'req': []},
    2310: {'tier': 0, 'name': 'Noble Gas', 'type_id': 2310, 'req': []},
    2311: {'tier': 0, 'name': 'Reactive Gas', 'type_id': 2311, 'req': []},
    # P1
    2389: {'tier': 1, 'name': 'Plasmoids', 'type_id': 2389, 'req': [2308]},
    2390: {'tier': 1, 'name': 'Electrolytes', 'type_id': 2390, 'req': [2309]},
    2392: {'tier': 1, 'name': 'Oxidizing Compound', 'type_id': 2392, 'req': [2311]},
    2393: {'tier': 1, 'name': 'Bacteria', 'type_id': 2393, 'req': [2073]},
    2396: {'tier': 1, 'name': 'Biofuels', 'type_id': 2396, 'req': [2288]},
    2397: {'tier': 1, 'name': 'Industrial Fibers', 'type_id': 2397, 'req': [2305]},
    2398: {'tier': 1, 'name': 'Reactive Metals', 'type_id': 2398, 'req': [2267]},
    2399: {'tier': 1, 'name': 'Precious Metals', 'type_id': 2399, 'req': [2310]},
    2400: {'tier': 1, 'name': 'Toxic Metals', 'type_id': 2400, 'req': [2306]},
    2401: {'tier': 1, 'name': 'Chiral Structures', 'type_id': 2401, 'req': [2306]},
    3645: {'tier': 1, 'name': 'Water', 'type_id': 3645, 'req': [2268]},
    3683: {'tier': 1, 'name': 'Oxygen', 'type_id': 3683, 'req': [2310]},
    3779: {'tier': 1, 'name': 'Biomass', 'type_id': 3779, 'req': [2286]},
    9828: {'tier': 1, 'name': 'Silicon', 'type_id': 9828, 'req': [2307]},
    # P2
    44: {'tier': 2, 'name': 'Enriched Uranium', 'type_id': 44, 'req': [2399, 2400]},
    2312: {'tier': 2, 'name': 'Supertensile Plastics', 'type_id': 2312, 'req': [3683, 3779]},
    2317: {'tier': 2, 'name': 'Oxides', 'type_id': 2317, 'req': [3683, 2392]},
    2327: {'tier': 2, 'name': 'Microfiber Shielding', 'type_id': 2327, 'req': [2397, 9828]},
    2329: {'tier': 2, 'name': 'Biocells', 'type_id': 2329, 'req': [2396, 2399]},
    2463: {'tier': 2, 'name': 'Nanites', 'type_id': 2463, 'req': [2393, 2398]},
    3689: {'tier': 2, 'name': 'Mechanical Parts', 'type_id': 3689, 'req': [2398, 2399]},
    9832: {'tier': 2, 'name': 'Coolant', 'type_id': 9832, 'req': [2390, 3645]},
    9836: {'tier': 2, 'name': 'Consumer Electronics', 'type_id': 9836, 'req': [2400, 2401]},
    9838: {'tier': 2, 'name': 'Superconductors', 'type_id': 9838, 'req': [2389, 3645]},
    # P3
    2348: {'tier': 3, 'name': 'Gel-Matrix Biopaste', 'type_id': 2348, 'req': [3683, 2329, 9838]},
    9848: {'tier': 3, 'name': 'Robotics', 'type_id': 9848, 'req': [3689, 9836]},
    17392: {'tier': 3, 'name': 'Data Chips', 'type_id': 17392, 'req': [2312, 2327]},
}

SCHEMATICS = {i: {'id': i, 'name': n, 'cycle': c} for i, n, c in [
    # schematicID schematicName   cycleTime
    (65, "Superconductors", 3600),
    (66, "Coolant", 3600),
    (67, "Rocket Fuel", 3600),
    (68, "Synthetic Oil", 3600),
    (69, "Oxides", 3600),
    (70, "Silicate Glass", 3600),
    (71, "Transmitter", 3600),
    (72, "Water-Cooled CPU", 3600),
    (73, "Mechanical Parts", 3600),
    (74, "Construction Blocks", 3600),
    (75, "Enriched Uranium", 3600),
    (76, "Consumer Electronics", 3600),
    (77, "Miniature Electronics", 3600),
    (78, "Nanites", 3600),
    (79, "Biocells", 3600),
    (80, "Microfiber Shielding", 3600),
    (81, "Viral Agent", 3600),
    (82, "Fertilizer", 3600),
    (83, "Genetically Enhanced Livestock", 3600),
    (84, "Livestock", 3600),
    (85, "Polytextiles", 3600),
    (86, "Test Cultures", 3600),
    (87, "Supertensile Plastics", 3600),
    (88, "Polyaramids", 3600),
    (89, "Ukomi Superconductor", 3600),
    (90, "Condensates", 3600),
    (91, "Camera Drones", 3600),
    (92, "Synthetic Synapses", 3600),
    (94, "High-Tech Transmitter", 3600),
    (95, "Gel-Matrix Biopaste", 3600),
    (96, "Supercomputers", 3600),
    (97, "Robotics", 3600),
    (98, "Smartfab Units", 3600),
    (99, "Nuclear Reactors", 3600),
    (100, "Guidance Systems", 3600),
    (102, "Neocoms", 3600),
    (103, "Planetary Vehicles", 3600),
    (104, "Biotech Research Reports", 3600),
    (105, "Vaccines", 3600),
    (106, "Industrial Explosives", 3600),
    (107, "Hermetic Membranes", 3600),
    (108, "Transcranial Microcontroller", 3600),
    (109, "Data Chips", 3600),
    (110, "Hazmat Detection Systems", 3600),
    (111, "Cryoprotectant Solution", 3600),
    (112, "Organic Mortar Applicators", 3600),
    (113, "Sterile Conduits", 3600),
    (114, "Nano-Factory", 3600),
    (115, "Self-Harmonizing Power Core", 3600),
    (116, "Recursive Computing Module", 3600),
    (117, "Broadcast Node", 3600),
    (118, "Integrity Response Drones", 3600),
    (119, "Wetware Mainframe", 3600),
    (121, "Water", 1800),
    (122, "Plasmoids", 1800),
    (123, "Electrolytes", 1800),
    (124, "Oxygen", 1800),
    (125, "Oxidizing Compound", 1800),
    (126, "Reactive Metals", 1800),
    (127, "Precious Metals", 1800),
    (128, "Toxic Metals", 1800),
    (129, "Chiral Structures", 1800),
    (130, "Silicon", 1800),
    (131, "Bacteria", 1800),
    (132, "Biomass", 1800),
    (133, "Proteins", 1800),
    (134, "Biofuels", 1800),
    (135, "Industrial Fibers", 1800),
]}

SIZES = (0.01, 0.38, 1.5, 6)
for v in ITEMS.values():
    v['size'] = SIZES[v['tier']]

SPACE = {'Launchpad': 10000, 'Storage': 12000}

with open('/home/zigdon/.everc') as f:
    ACCOUNTS = []
    for line in f:
        char_id, key_id, vcode, keywords = line.split(',', 3)
        char_id = int(char_id)
        key_id = int(key_id)
        vcode = vcode.strip()
        keywords = keywords.lower().strip().split(',')
        ACCOUNTS.append((char_id, key_id, vcode, keywords))
    f.close()

def get_journal_tx():
    """Parse tx log, detecting bounties and taxes."""
    journal, _, _ = char.wallet_journal(limit=500)

    def blank_tx():
        """Template for a new transaction."""
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

def add_market_tx(tx_cats):
    """Read transactions, optionally export tsv."""

    transactions, _, _ = char.wallet_transactions()

    export_fd = None
    if FLAGS.export_tx:
        export_fd = open(FLAGS.export_tx, 'a')

    for transaction in transactions:
        timestamp = datetime.datetime.fromtimestamp(transaction['timestamp'])
        day = timestamp.date()

        if export_fd:
            export_fd.write('\t'.join([timestamp.strftime('%x %X'),
                                       str(transaction['quantity']),
                                       transaction['type']['name'],
                                       '%.2f' % transaction['price']]))
            export_fd.write('\n')

        if transaction['action'] == 'buy':
            tx_cats[day]['purchases'] += transaction['price'] * transaction['quantity']
        elif transaction['action'] == 'sell':
            tx_cats[day]['sales'] += transaction['price'] * transaction['quantity']

    if export_fd:
        export_fd.close()

def get_contracts(timeout=0):
    """Load the recent character contracts."""
    contracts, _, _ = char.contracts()
    contracts = contracts.values()

    if timeout:
        now = time.mktime(datetime.datetime.utcnow().timetuple())
        contracts = [c for c in contracts
                     if c['status'] != 'Completed'
                     or c['issued'] > now - timeout]

    if contracts:
        char_ids = set([c['issuer'] for c in contracts])
        char_ids.update(set([c['assignee'] for c in contracts]))
        names, _, _ = evelink.eve.EVE().character_names_from_ids(char_ids)

        print '%20s | %20s | %20s | %12s | %s' % (
            'When', 'From', 'To', 'Amount', 'Status'
        )
        print '-'*90
        for contract in sorted(contracts, key=operator.itemgetter('issued')):
            print '%20s | %20s | %20s | %14s | %s' % (
                datetime.datetime.fromtimestamp(contract['issued']),
                names[contract['issuer']],
                names[contract['assignee']],
                humanize.intcomma(int(contract['price'])),
                contract['status'])

def search_calendar(keyword_list):
    """Search for listed keywords in calendar entries."""
    cal_items = char.calendar_events()
    items = []
    for _, event in cal_items[0].iteritems():
        for keyword in keyword_list:
            if keyword in event['title'].lower():
                start = humanize.naturalday(
                    datetime.datetime.fromtimestamp(event['start_ts']))

                items.append('%s - %s' % (start, event['title']))

    return items

def get_planetary_alerts():
    """Examine PI, find and report shortages and other warnings."""
    planets, _, _ = char.planetary_colonies()
    planet_alerts = OrderedDict()

    def name(type_id):
        """Utility to translate id to name."""
        return ITEMS[type_id]['name']

    def get_pin_type(name):
        """Utility to extract a building type from its name."""
        return name.split()[1]

    def blank_planet():
        """Default entry for a new planet."""
        return {
            'needs': defaultdict(int),  # id: qty/hr
            'makes': defaultdict(int),  # id: qty/hr
            'has': defaultdict(int),    # id: qty
            'counts': defaultdict(int), # id: number
        }

    def planet_summary(data):
        """Given a record for a planet, print out a human readable summary."""
        for section in ('makes', 'has', 'needs'):
            print '  %s:' % section.upper()
            for resource in sorted(data[section],
                                   key=lambda x: (ITEMS[x]['tier'], name(x))):
                if section != 'has' and name(resource) in data['counts']:
                    count = data['counts'][name(resource)]
                    name_and_count = '%dx %s' % (count, name(resource))
                else:
                    name_and_count = '   %s' % name(resource)
                print '    %-21s %d (%d m3) [%s]' % (
                    name_and_count, data[section][resource],
                    ITEMS[resource]['size'] * data[section][resource],
                    ', '.join([name(x) for x in ITEMS[resource]['req']])
                )

    def find_yield(state, item_id, bottlenecks=None):
        """Recursively examine a planet's production, finding overall yield."""
        if bottlenecks is None:
            bottlenecks = []
        reqs = [x for x in ITEMS[item_id]['req'] if x in state['makes']]
        if reqs:
            ratios = []
            for req in reqs:
                make, bottlenecks = find_yield(state, req, bottlenecks)
                if state['needs'][req]:
                    ratio = (0.0 + make + state['has'][req])/state['needs'][req]
                else:
                    ratio = 1

                if FLAGS.debug:
                    print ('%s: makes %d, has: %d, needs: %d, '
                           'ratio: %f, bottlenecks: %s' % (
                               ITEMS[req]['name'], make, state['has'][req],
                               state['needs'][req], ratio, bottlenecks))

                if ratio < 1.0:
                    bottlenecks.append(
                        '%s (%d%%)' % (ITEMS[req]['name'], 100.0*ratio))
                ratios.append(ratio)
            ratio = min(ratios + [1.0])
        else:
            ratio = 1.0

        if FLAGS.debug_planet:
            print 'Checking bottlenecks for %s: makes %d, has %d (%d).' % (
                name(item_id),
                ratio * state['makes'][item_id],
                state['has'][item_id],
                ratio * 100)
        return ratio * state['makes'][item_id], bottlenecks

    planet_state = defaultdict(blank_planet)

    for planet_id, planet_info in planets.items():
        planet_name = '%s: %s' % (
            planet_info['planet']['type_name'],
            planet_info['planet']['name'])

        if FLAGS.debug_planet and FLAGS.debug_planet not in planet_name:
            print 'Skipping %s.' % planet_name
            continue

        planet_alerts[planet_name] = []
        routes, _, _ = char.planetary_routes(planet_id)
        route_map = char.planetary_route_map(routes)
        pins, _, _ = char.planetary_pins(planet_id)
        now = datetime.datetime.now()
        for pin in pins.values():
            pin_type = get_pin_type(pin['type']['name'])
            schematic = pin['schematic']

            if schematic in SCHEMATICS:
                schematic_name = SCHEMATICS[schematic]['name']
                planet_state[planet_id]['counts'][schematic_name] += 1

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
                        continue


                    if pin_type == 'Extractor':
                        planet_state[planet_id]['makes'][type_id] += qty
                    elif route['source_id'] == pin['id']:
                        qty *= -1

                    if pin_type == 'Basic':
                        qty *= 2

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

        if FLAGS.show_state or FLAGS.debug_planet:
            print "\n\nState for %s:\n" % planet_name
            planet_summary(planet_state[planet_id])

        if FLAGS.debug:
            pprint(planet_state)

        # check that we have what we need for the next day
        alert = None
        tier = max([ITEMS[x]['tier'] for x in planet_state[planet_id]['makes']])
        for item_id in planet_state[planet_id]['makes']:
            if ITEMS[item_id]['tier'] != tier:
                continue

            pi_yield, bottlenecks = find_yield(planet_state[planet_id], item_id)
            if bottlenecks:
                ratio = 100.0 * pi_yield / planet_state[planet_id]['makes'][item_id]
                planet_alerts[planet_name].append(
                    'Manufacturing %s at %d%% capacity: %r' % (
                        ITEMS[item_id]['name'], ratio, bottlenecks))



        if alert is not None:
            planet_alerts[planet_name].append(alert)

    return planet_alerts

_ = FLAGS(sys.argv)

if FLAGS.export_tx:
    try:
        os.unlink(FLAGS.export_tx)
    except OSError:
        pass

for char_id, key_id, vcode, keywords in ACCOUNTS:
    api = evelink.api.API(api_key=(key_id, vcode),
                          cache=evelink.cache.sqlite.SqliteCache(
                              '/tmp/evecache-wallet.sq3'))
    char = evelink.char.Char(char_id=char_id, api=api)
    sheet, _, _ = char.character_sheet()

    char_name = sheet['name'].upper()

    if FLAGS.debug_char is not None:
        if FLAGS.debug_char.upper() not in char_name:
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

    get_contracts(2*24*60*60)

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

    if FLAGS.transaction_details:
        print 'Transaction details:\n'
        for entry in tx_details:
            print '{date} | {party:26} | {amount:13,} | {balance:16,} | {reason}'.format(**entry)
