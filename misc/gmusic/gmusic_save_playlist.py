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

print "#EXTM3U"
for t in playlist['tracks']:
    if 'track' not in t:
      info = titles[t['trackId']]
    else:
      info = t['track']

    print "#EXTINF:%d,%s - %s" % (int(info['durationMillis'])/999,
                                  info['artist'],
                                  info['title'])
