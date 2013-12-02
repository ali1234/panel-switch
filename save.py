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


props = result.get_child_value(0)

for n in range(props.n_children()):
    p = props.get_child_value(n)
    pp = p.get_child_value(0).get_string()
    pv = p.get_child_value(1).get_variant()

    pn = GLib.Variant.parse(None, str(pv), None, None)
    assert(pv == pn)

    print(pp, pv)

