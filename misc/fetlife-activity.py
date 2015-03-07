#!env python

import sys
sys.path.insert(0, '/home/zigdon/lib/code/github/zigdon/'
                   'misc/fetlife/lib/python2.7/site-packages')
import argparse
from datetime import datetime
import logging
import lxml.html
import os
import parsedatetime as pdt
import mechanize
import re

from BeautifulSoup import BeautifulSoup

parser = argparse.ArgumentParser(description='Get activity feed from FetLife')
parser.add_argument('--debug', '-n', action='store_true')
parser.add_argument('--date')
parser.add_argument('--last_run')
parser.add_argument('rc')

args = parser.parse_args()

logger = logging.getLogger('mechanize')
logger.addHandler(logging.StreamHandler(sys.stdout))
#logger.setLevel(logging.DEBUG)

cal = pdt.Calendar()

def cal_to_dt(d):
    d = cal.parse(d)[0]
    return datetime(d.tm_year, d.tm_mon, d.tm_mday, d.tm_hour,
                    d.tm_min, d.tm_sec)

# load activity since yesterday
if args.date:
    last_run = cal_to_dt(args.date)
elif args.last_run and os.path.isfile(args.last_run):
    stat = os.stat(args.last_run)
    last_run = datetime.fromtimestamp(stat.st_mtime)
else:
    last_run = cal_to_dt('yesterday')

if not args.debug:
# load creds
    with open(args.rc) as f:
        username = f.next().strip()
        password = f.next().strip()
        watch = f.next().strip()

# create browser
    br = mechanize.Browser()
    br.set_handle_robots(False)

# load login page
    br.open('https://fetlife.com/login')

# enter login details
    br.select_form(nr=0)
    br.form.new_control('text', 'nickname_or_email', {'value': username})
    br.form.new_control('password', 'password', {'value': password})

# log in
    resp = br.submit()

# download xls
    br.open('https://fetlife.com/users/%d/activity' % int(watch))
    html = br.response().read()

    with open('/tmp/debug.html', 'w') as f:
      f.write(html)

else:
    with open('/tmp/debug.html', 'r') as f:
      html = f.read()

tree = BeautifulSoup(html)
feed = tree.find(id='mini_feed')
for item in feed.findAll('li'):
    (kind, link, text, body, when) = (None, item.a['href'], None, None, None)

    title = item.span.text
    if 'own status' in title:
        kind = 'comment_own_status'
        link = item.blockquote.a['href']
        title = 'commented on their status'
        if item.blockquote.a is not None:
            item.blockquote.a.string = ''
        body = item.blockquote.text
    elif title.startswith('commented on') and 'writing' in title:
        kind = 'comment_writing'
        post = item.findAll('a')[2]
        title = "commented on %s's writing: %s" % (item.a.text, post.text)
        link = post['href']
        comment = item.blockquote
        if comment.a is not None:
            comment.a.string = ''
        body = comment.text
    elif title.startswith('commented on') and 'picture' in title:
        kind = 'comment_picture'
        link = item.findAll('span')[2].a['href']
        title = "commented on %s's picture" % item.a.text
        comment = item.findAll('span')[3]
        if comment.a is not None:
            comment.a.string = ''
        body = comment.text
    elif title.startswith('commented on') and 'status' in title:
        kind = 'comment_status'
        title = "commented on %s's status" % item.a.text
        link = item.findAll('a')[1]['href']
        if item.blockquote.a is not None:
            item.blockquote.a.string = ''
        body  = item.blockquote.text
    elif title.startswith('joined the group'):
        kind = 'joined'
        title = 'joined a group: %s' % item.a.text
    elif title.startswith('wrote on'):
        kind = 'wrote_wall'
        title = "%s's wall" % item.a.text
        if item.blockquote.a is not None:
            item.blockquote.a.string = ''
        body = item.blockquote.text
    elif title.startswith('loved one of'):
        kind = 'loved'
        link = item.findAll('a')[1]['href']
        title = "%s's post" % item.a.text
    elif title.startswith('is going to'):
        kind = 'going'
        title = item.a.text
    elif title.startswith('might be going'):
        kind = 'might_go'
        title = item.a.text
    elif title.startswith('uploaded a new picture'):
        kind = 'new_picture'
        title = item.img['alt']
    elif title.startswith('went from might be going to is going to'):
        kind = 'now_going'
        title = item.a.text
    elif (title.startswith('updated his writing')
          or title.startswith('updated her writing')):
        kind = 'updated_writing'
        title = 'Updated their post: %s' % item.a.text
    elif re.match(r'\d* days ago$', title):
        kind = 'friend'
        when = item.span.text
        title = 'Friended %s' % item.a.text
    else:
        kind = 'status'
        title = title

    if when is None:
        when = item.findAll('span')[1].text

    if 'fetlife.com' in link:
        link = 'https://fetlife.com/%s' % link.split('/', 3)[3]
    else:
        link = 'https://fetlife.com%s' % link

    if cal_to_dt(when) < last_run:
        break

    print """
    Title: %s
    When: %s

    """ % (lxml.html.fromstring(title).text, when)

    if body is not None:
        print lxml.html.fromstring(body).text

    print "%s\n" % link

if args.last_run:
    with open(args.last_run, "w") as f:
        f.write(str(datetime.now()))


