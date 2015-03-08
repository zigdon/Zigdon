#!/usr/bin/python

import argparse
from email.mime.text import MIMEText
import os
import smtplib
import twitter

parser = argparse.ArgumentParser(description='Follow a weechat log, watch for a'
                                 ' username email matches.')
parser.add_argument('--user')
parser.add_argument('--to_email')
parser.add_argument('--from_email')
parser.add_argument('--smtp')
parser.add_argument('--rc')
parser.add_argument('--last_id')

args = parser.parse_args()

last_id = None

with open(args.rc) as f:
    consumer_key = f.readline().strip()
    consumer_secret = f.readline().strip()
    access_token_key = f.readline().strip()
    access_token_secret = f.readline().strip()

api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token_key,
                  access_token_secret=access_token_secret)

if not api.VerifyCredentials():
    raise Exception('Invalid credentials.')

if args.last_id and os.path.isfile(args.last_id):
    with open(args.last_id) as f:
        last_id = f.read().strip()

if last_id:
    statuses = api.GetUserTimeline(args.user,
                                   exclude_replies=True,
                                   include_rts=False,
                                   since_id=last_id)
else:
    statuses = api.GetUserTimeline(args.user,
                                   exclude_replies=True,
                                   include_rts=False)

last_id = None
message = ''
for s in reversed(statuses):
    if s.text[0] == '@':
        continue

    message += """
    at: %s

    %s

    http://twitter.com/%s/status/%s



    """ % (s.created_at, s.text, s.user.screen_name, s.id)
    last_id = s.id

if message:
    if args.smtp:
        msg = MIMEText(message.encode('UTF-8'))
        msg['Subject'] = 'Twitter updates'
        msg['From'] = args.from_email
        msg['To'] = args.to_email
        s = smtplib.SMTP(args.smtp)
        s.set_debuglevel(0)
        s.sendmail(args.from_email,
                [args.to_email],
                msg.as_string())
        s.quit()
    else:
        print message

if last_id is not None and args.last_id:
    with open(args.last_id, 'w') as f:
        f.write(str(last_id))
