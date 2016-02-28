"""
Displays Info About Windows Portable Executables
"""

from yapsy.IPlugin import IPlugin

import pefile


class FaPefile(IPlugin):
    def __init__(self):
        self._display_name = 'PE File'
        self._popularity = 5
        self._parent = False
        self._cache = True 
        IPlugin.__init__(self)

    def activate(self):
        IPlugin.activate(self)
        return

    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def check(self, evidence, path_on_disk):
        """Checks if the file is compatable with this plugin"""
        allowed = ['application/x-dosexec']
        return str(evidence['mimetype']).lower() in allowed

    def mimetype(self, mimetype):
        """Returns the mimetype of this plugins get command"""
        return "text/plain"

    def get(self, evidence, helper, path_on_disk, request, children):
        """Returns the result of this plugin to be displayed in a browser"""
        try:
            pe = pefile.PE(path_on_disk)
            return '<xmp style="white-space: pre-wrap;">\n' + pe.dump_info() + "</xmp>"
        except Exception as e:
            return '<xmp style="white-space: pre-wrap;">error parsing file: ' + str(path_on_disk) + "Got the following error: " + str(e) + "</xmp>"
