#!/usr/bin/env python
# coding: utf-8
import sys
from gmusicapi import Mobileclient
from pprint import pprint

with open("/home/zigdon/.gmusicrc") as f:
    user, pw = [(x.split('='))[1].strip() for x in f.readlines()]

mc = Mobileclient()
mc.login(user,pw, Mobileclient.FROM_MAC_ADDRESS)
pl = mc.get_all_user_playlist_contents()

playlist = None
if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    pl = [x for x in pl if arg in x['id'].lower() or arg in x['name'].lower()]
    if len(pl) == 1:
        playlist = pl[0]

    print 'Analysing playlist: %s' % playlist['name']

if not playlist:
    print 'Playlist ID or name are required.'
    for p in pl:
        print '%20s - %s' % (p['id'], p['name'])
    sys.exit(1)

if 'tracks' not in playlist:
    print 'No tracks found!'
    sys.exit(1)

songs = mc.get_all_songs()
titles = {x['id']: x for x in songs}

for t in playlist['tracks']:
    if 'track' not in t:
      info = titles[t['trackId']]
      print ">>> %31.29s / %.20s / \"%.30s\"" % (info['album'], info['artist'], info['title'])
    else:
      info = t['track']
      print "%35.33s / %.20s / \"%.30s\"" % (info['album'], info['artist'], info['title'])

missing = []
for t in playlist['tracks']:
    if 'track' not in t:
      info = titles[t['trackId']]
    if 'nid' not in t or t['nid'][0] != 'T':
      missing.append(info)

def summary(track):
    print title(track)
    if 'nid' in track and track['nid'].startswith('T'):
        print 'https://play.google.com/music/m/%s' % track['nid']

def title(track):
    return "%35.33s / %.20s / \"%.20s\"" % (track['album'], track['artist'], track['title'])

nomatch = ''
toomany = []
found = []
for t in missing:
    res = (mc.search_all_access('"%s" "%s"' % (t['artist'], t['title'])))['song_hits']
    if len(res) == 0:
      nomatch += title(t) + "\n"
      continue
    if t['nid'] in [x['track'].get('nid', None) for x in res]:
      found.append(title(t))
      continue
    if len(res) < 10:
      summary(t)
      print '-' * 80
      print "%d possible suggestions:" % len(res)
      for r in res:
        summary(r['track'])
      print "\n\n"
      continue
    toomany.append((title(t), len(res)))
print "No matches for the following:"
print nomatch
print "\n\n"
print "Found these in AA after all:"
for r in found:
    print r
print "\n\n"
print "Too many results for the following:"
for r in toomany:
    print "%3d %s" % (r[1], r[0])
