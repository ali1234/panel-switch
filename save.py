#!/usr/bin/env python3

import gi.repository
from gi.repository import Gio, GLib

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

result = xfconf.call_sync('GetAllProperties', GLib.Variant('(ss)', ('xfce4-panel', '')), 0, -1, None)

props = [(k,v) for k,v in result[0].items()]
props.sort()

for k,v in props:
    print(k,repr(v))

