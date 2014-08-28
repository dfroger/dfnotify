#!/usr/bin/env python
import datetime
import os
import ConfigParser

from lockfile import FileLock, LockTimeout

POMODORO_FILE = os.path.expanduser('~/.pomodoro')
POMODORO_LOCK = FileLock(POMODORO_FILE)
POMODORO_SOUND = os.path.expanduser('~/bell.ogg')

def read_pomodoro():
    """Read pomodoro data in ~/.pomodoro"""
    filename = os.path.expanduser('~/.pomodoro')

    while not POMODORO_LOCK.i_am_locking():
        try:
            POMODORO_LOCK.acquire(timeout=1)
        except LockTimeout:
            POMODORO_LOCK.break_lock()
            POMODORO_LOCK.acquire()

    parser = ConfigParser.ConfigParser()
    parser.read(POMODORO_FILE)
    d = {}

    d['date'] = {}
    d['date']['start'] = datetime.datetime.strptime( parser.get('date','start') ,'%Y-%m-%d %H:%M:%S')

    d['display'] = {}
    d['display']['visible'] = parser.get('display','visible')

    d['sound'] = {}
    d['sound']['play'] = parser.get('sound','play')
    d['sound']['played'] = parser.get('sound','played')
    d['sound']['file'] = parser.get('sound','file')

    POMODORO_LOCK.release()

    return d

def new_pomodoro():
    now = datetime.datetime.now()
    start = now.strftime('%Y-%m-%d %H:%M:%S')

    d = {}
    d['date'] = {'start' : start}
    d['display'] = {'visible':'1'}
    d['sound'] = {'play':'1', 'played':0, 'file':POMODORO_SOUND}
    return d

def write_pomodoro(d):
    """Write pomodoro data in ~/.pomodoro"""
    config = ConfigParser.RawConfigParser()
    for section,items in d.iteritems():
        config.add_section(section)
        for name,value in items.iteritems():
            config.set(section,name,value)

    while not POMODORO_LOCK.i_am_locking():
        try:
            POMODORO_LOCK.acquire(timeout=1)
        except LockTimeout:
            POMODORO_LOCK.break_lock()
            POMODORO_LOCK.acquire()

    with open(POMODORO_FILE,'w') as f:
        config.write(f)

    POMODORO_LOCK.release()

if __name__ == '__main__':
    p = new_pomodoro()
    write_pomodoro(p)
