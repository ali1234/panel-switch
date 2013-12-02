#!/usr/bin/env python3

import gi.repository
from gi.repository import Gio, GLib
import sys, os

session_bus = Gio.BusType.SESSION
cancellable = None
connection = Gio.bus_get_sync(session_bus, cancellable)

proxy_property = 0
interface_properties_array = None
destination = 'org.xfce.Xfconf'
path = '/org/xfce/Xfconf'
interface = destination

xfconf = Gio.DBusProxy.new_sync(
     connection,
     proxy_property,
     interface_properties_array,
     destination,
     path,
     interface,
     cancellable)

os.system('killall xfce4-panel')

try:
    result = xfconf.call_sync('ResetProperty', GLib.Variant('(ssb)', ('xfce4-panel', '/', True)), 0, -1, None)
except:
    pass

f = open(sys.argv[1])

for line in f:
    x = line.strip().split(' ', 1)
    print(x)
    result = xfconf.call_sync('SetProperty', GLib.Variant('(ssv)', ('xfce4-panel', x[0], GLib.Variant.parse(None, x[1], None, None))), 0, -1, None)

os.system('cd ~ && xfce4-panel &')
