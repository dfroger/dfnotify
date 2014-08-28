#!/usr/bin/python
import dbus
import time
from dzen2_bar import read_pomodoro, format_pomodoro

def get_dbus ():
    bus = dbus.SessionBus()
    obj = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
    purple = dbus.Interface(obj, "im.pidgin.purple.PurpleInterface")
    return purple

def pidgin_status(message, purple):
    old_status = purple.PurpleSavedstatusGetCurrent()               # get current status
    status_type = purple.PurpleSavedstatusGetType(old_status)       # get current status type
    new_status = purple.PurpleSavedstatusNew("", status_type)       # create new status with old status type
    purple.PurpleSavedstatusSetMessage(new_status, message)  # fill new status with status message
    purple.PurpleSavedstatusActivate(new_status)                    # activate new status

purple = get_dbus()

while True:

    d = read_pomodoro()
    t = format_pomodoro(d)[:5]

    #msg = "%s / 25:00 [X] [ ] [ ] [ ] coffee!" % t
    if t == "00:00":
        msg = ""
    else:
        msg = "Pomodoro: %s / 25:00 " % t

    print msg
    pidgin_status (msg, purple)

    time.sleep(5)
