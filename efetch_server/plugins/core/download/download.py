"""
A simple plugin that starts a download of the file
"""

from yapsy.IPlugin import IPlugin
from bottle import static_file
import os


class Download(IPlugin):
    def __init__(self):
        self.display_name = 'Download'
        self.popularity = 1
        self.cache = True
        self.fast = False
        self.action = False
        self.icon = 'fa-download'
        IPlugin.__init__(self)

    def activate(self):
        IPlugin.activate(self)
        return

    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def check(self, evidence, path_on_disk):
        """Checks if the file is compatible with this plugin"""
        return path_on_disk and evidence['meta_type'] == 'File'

    def mimetype(self, mimetype):
        """Returns the mimetype of this plugins get command"""
        return mimetype

    def get(self, evidence, helper, path_on_disk, request):
        """Returns the result of this plugin to be displayed in a browser"""
        return static_file(os.path.basename(path_on_disk), root=os.path.dirname(path_on_disk),
                           download=os.path.basename(path_on_disk))
