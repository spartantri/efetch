"""
Displays all files, folders, and timeline events using a list view
"""

from yapsy.IPlugin import IPlugin



class FaTimelinelist(IPlugin):

    def __init__(self):
        self.display_name = 'Timeline List'
        self.popularity = 0
        self.parent = True
        self.cache = False
        IPlugin.__init__(self)

    def activate(self):
        IPlugin.activate(self)
        return

    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def check(self, evidence, path_on_disk):
        """Checks if the file is compatable with this plugin"""
        return True

    def mimetype(self, mimetype):
        """Returns the mimetype of this plugins get command"""
        return "text/plain"

    def get(self, evidence, helper, path_on_disk, request, children):
        """Returns the result of this plugin to be displayed in a browser"""
        return helper.plugin_manager.getPluginByName('fa_timeline').plugin_object.get(evidence,
                                                                                     helper, path_on_disk, request,
                                                                                     children, True, True, True,
                                                                                      True, 'fa_timelinelist',
                                                                                      self.display_name)
