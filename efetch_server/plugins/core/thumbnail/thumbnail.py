"""
Returns a thumbnail or icon of the specified file
"""

from yapsy.IPlugin import IPlugin
from bottle import static_file
import os


class Thumbnail(IPlugin):
    def __init__(self):
        self.display_name = 'Thumbnail'
        self.popularity = 0
        self.cache = False
        self.fast = True
        self.action = True
        IPlugin.__init__(self)

    def activate(self):
        IPlugin.activate(self)
        return

    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def check(self, evidence, path_on_disk):
        """Checks if the file is compatible with this plugin"""
        return True

    def mimetype(self, mimetype):
        """Returns the mimetype of this plugins get command"""
        return "text/plain"

    def get(self, evidence, helper, path_on_disk, request):
        """Returns either an icon or thumbnail of the provided file"""
        # If it is folder just return the folder icon
        if evidence['meta_type'] == 'Directory' or unicode(evidence['file_name']).strip() == "." or unicode(
                evidence['file_name']).strip() == "..":
            return static_file("_folder.png", root=helper.icon_dir, mimetype='image/png')
        if evidence['meta_type'] != 'File':
            return static_file("_blank.png", root=helper.icon_dir, mimetype='image/png')

        # If the file is an image create a thumbnail
        if evidence['mimetype'].startswith('image'):
            # Cache file
            # helper.pathspec_helper.cache_file(evidence['pathspec'])
            helper.pathspec_helper.create_thumbnail(evidence)
            thumbnail_cache_path = evidence['thumbnail_cache_path']
            thumbnail_cache_dir = evidence['thumbnail_cache_dir']

            if os.path.isfile(thumbnail_cache_path):
                return static_file(evidence['file_name'], root=thumbnail_cache_dir)
            else:
                return static_file('_missing.png', root=helper.icon_dir, mimetype='image/png')
        # If file is not an image return the icon associated with the files extension
        else:
            if not os.path.isfile(helper.icon_dir + str(evidence['extension']).lower() + ".png"):
                return static_file("_blank.png", root=helper.icon_dir, mimetype='image/png')
            else:
                return static_file(evidence['extension'].lower() + ".png", root=helper.icon_dir, mimetype='image/png')