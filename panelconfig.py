#!/usr/bin/env python3

from gi.repository import Gio, GLib
import tarfile
import io
import time
import os

from os.path import expanduser

def add_to_tar(t, bytes, arcname):
    ti = tarfile.TarInfo(name=arcname)
    ti.size = len(bytes)
    ti.mtime = time.time()
    f = io.BytesIO(bytes)
    t.addfile(ti, fileobj=f)

class PanelConfig(object):
    def __init__(self):
        self.desktops = []
        self.properties = {}

    def from_xfconf(xfconf):
        pc = PanelConfig()

        result = xfconf.call_sync('GetAllProperties', GLib.Variant('(ss)', ('xfce4-panel', '')), 0, -1, None)

        props = result.get_child_value(0)

        for n in range(props.n_children()):
            p = props.get_child_value(n)
            pp = p.get_child_value(0).get_string()
            pv = p.get_child_value(1).get_variant()

            pn = GLib.Variant.parse(None, str(pv), None, None)
            assert(pv == pn)

            pc.properties[pp] = pv

        pc.find_desktops()

        pc.source = None

        return pc

    def from_file(filename):
        pc = PanelConfig()

        pc.source = tarfile.open(filename, mode='r')
        config = pc.source.extractfile('config.txt')

        for line in config:
            x = line.decode('utf-8').strip().split(' ', 1)
            pc.properties[x[0]] = GLib.Variant.parse(None, x[1], None, None)

        pc.find_desktops()

        return pc

    def find_desktops(self):
        for pp,pv in self.properties.items():
            path = pp.split('/')
            if len(path) == 3 and path[0] == '' and path[1] == 'plugins' and path[2].startswith('plugin-'):
                number = path[2].split('-')[1]
                if pv.get_type_string() == 's' and pv.get_string() == 'launcher':
                   for d in self.properties['/plugins/plugin-'+number+'/items'].unpack():
                       self.desktops.append('launcher-'+number+'/'+d)

    def get_desktop_source_file(self, desktop):
        if self.source == None:
            return open(expanduser("~")+'/.config/xfce4/panel/'+desktop, 'rb')
        else:
            return self.source.extractfile(desktop)

    def to_file(self, filename):
        if filename.endswith('.gz'):
            mode = 'w:gz'
        elif filename.endswith('.bz2'):
            mode = 'w:bz2'
        else:
            mode = 'w'
        t = tarfile.open(name=filename, mode=mode)
        props_tmp = []
        for (pp,pv) in sorted(self.properties.items()):
            props_tmp.append(str(pp)+' '+str(pv))
        add_to_tar(t, '\n'.join(props_tmp).encode('utf8'), 'config.txt')

        for d in self.desktops:
            bytes = self.get_desktop_source_file(d).read()
            add_to_tar(t, bytes, d)

        t.close()

    def to_xfconf(self, xfconf):
        os.system('killall xfce4-panel')

        for (pp,pv) in sorted(self.properties.items()):
            result = xfconf.call_sync('SetProperty', GLib.Variant('(ssv)', ('xfce4-panel', pp, pv)), 0, -1, None)

        for d in self.desktops:
            bytes = self.get_desktop_source_file(d).read()
            f = open(expanduser("~")+'/.config/xfce4/panel/'+d, 'wb')
            f.write(bytes)
            f.close()

        os.system('cd ~ && xfce4-panel &')



if __name__=='__main__':

    import sys

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

    if len(sys.argv) != 3 or sys.argv[1] not in ['load', 'save']:
        print("""Panel Switch v0.1 - Usage:
panelconfig.py save <filename> : save current configuration.
panelconfig.py load <filename> : load configuration from file.
""")

    if sys.argv[1] == 'save':
        PanelConfig.from_xfconf(xfconf).to_file(sys.argv[2])
    elif sys.argv[1] == 'load':
        PanelConfig.from_file(sys.argv[2]).to_xfconf(xfconf)
