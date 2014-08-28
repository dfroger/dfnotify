#!/usr/bin/env python
import os
import subprocess
import datetime
import time
import logging
import logging.handlers
import traceback
import ConfigParser

import easyimap
import yaml

from pomodoro_start import *

def info(text):
    return r'^fg(grey80) %s' % text

def normal(text):
    return r'^fg(grey80) %s' % text

def alert(text):
    return r'^fg(red) %s' % text

def item_date():
    now = datetime.datetime.now()
    return normal( now.strftime("%A, %d %B %Y %H:%M") + ' ')

def get_unseen_emails(imap):
    unseen = imap.unseen(limit=10)
    to_me = []
    for email_id, email in unseen:
        if not email.to:
            continue
        if CONFIG['mail']['me'] in email.to.lower():
            to_me.append(email.from_addr)
    if to_me:
        sender = to_me[0]
        words = sender.split()
        if len(words) > 1:
            words = words[:-1]
        sender= ' '.join(words)
    else:
        sender = None

    return len(unseen), len(to_me), sender

def item_emails(imap):
    try:
        n_unseen,n_to_me,sender = get_unseen_emails(imap)
        if n_to_me == 0:
            return normal('[%i,%i]' % (n_unseen,n_to_me,))
        else:
            return alert( '[%i,%i,%s]' % (n_unseen,n_to_me,sender,) )
    except:
        logging.error( traceback.format_exc() )
        return alert('Emails error')

def item_pomodoro():
    try:
        d = read_pomodoro()
        return format_pomodoro(d)
    except:
        logging.error( traceback.format_exc() )
        return alert('Pomodoro error')

def pomodoro_play_sound(d):
    if d['sound']['play'] == '1' and d['sound']['played'] == '0':
        filename = os.path.expanduser(d['sound']['file'])
        subprocess.call(["mplayer", filename])
        d['sound']['played'] = '1'
        write_pomodoro(d)

def format_pomodoro(d):
    twentyfive_minutes = datetime.timedelta(minutes=25)
    total_seconds = 25*60

    if not d['display']['visible']:
        return ''

    now = datetime.datetime.now()
    end = d['date']['start'] + twentyfive_minutes
    remaining = end - now
    remaining_seconds = remaining.days*24*60*60 + remaining.seconds

    bar_length = 50

    if  remaining_seconds <= 0:
        minutes,seconds = 0,0
        p = "%2.2i:%2.2i^p(5)^ro(%ix5)"
        text = p % (minutes,seconds,bar_length)
        pomodoro_play_sound(d)
        return text
    elif remaining_seconds > total_seconds:
        raise ValueError, "pomodoro started in the future"
    else:
        minutes = remaining_seconds / 60
        seconds = remaining_seconds % 60

        p = "%2.2i:%2.2i^p(5)^ro(%ix5)^r(%ix5)"
        pct_remaining = float(remaining_seconds) / total_seconds
        length_remaining = pct_remaining * bar_length
        length_elapsed = bar_length - length_remaining
        text = p % (minutes,seconds,length_elapsed,length_remaining)
        return text

class Statusbar:

    def __init__(self,logger):
        args = 'dzen2 -ta r -bg black -fg grey80 -fn fixed'.split()
        self.dzen2 = subprocess.Popen(args,stdin=subprocess.PIPE)
        self.logger = logger

        imap_config = CONFIG['mail']['imap']
        self.imaps = {}
        for label,c in imap_config.iteritems():
            imap = easyimap.connect(host=c['host'], user=c['user'],
                                    password=c['password'], mailbox="INBOX",
                                    read_only=True)
            self.imaps[label] = imap

    def mainloop(self):
        self.logger.info('StatusBar: enter main loop')

        while True:
            try:
                line_list = []
                for label,imap in self.imaps.iteritems():
                    emails = item_emails(imap)
                    line_list.append("%s: %r" % (label,emails))

                line_list.append(item_pomodoro())
                line_list.append(item_date())

                line = normal(' | ').join(line_list)
                self.dzen2.stdin.write(line+'\n')
                self.dzen2.stdin.flush()

                time.sleep(30)

            except KeyboardInterrupt:
                self.logger.info('StatusBar:receive KeyboardInterrupt')
                break

        self.logger.info('StatusBar:exit main loop')


def main():

    logger = logging.getLogger("StatusbarLogger")
    logger.setLevel(logging.DEBUG)

    logfile = os.path.expanduser('~/dzen2_bar_py.log')

    handler = logging.handlers.RotatingFileHandler( \
        logfile,
        maxBytes=1024**2,
        backupCount=3)

    logger.addHandler(handler)

    bar = Statusbar(logger)
    bar.mainloop()

    logger.info('main: close application')

if __name__ == '__main__':
    CONFIG = yaml.load( open('config.yaml') )
    main()
