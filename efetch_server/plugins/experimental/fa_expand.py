"""
Navigates a new base evidence item, i.e. raw, E01, or zip file
"""

from yapsy.IPlugin import IPlugin
from yapsy.IPlugin import IPlugin
from jinja2 import Template


class FaExpand(IPlugin):

    def __init__(self):
        self.display_name = 'Expand'
        self.popularity = 8
        self.cache = False
        self.fast = False
        self.action = False
        self.icon = 'fa-hdd-o'
        IPlugin.__init__(self)

    def activate(self):
        IPlugin.activate(self)
        return

    def deactivate(self):
        IPlugin.deactivate(self)
        return

    def check(self, evidence, path_on_disk):
        """Checks if the file is compatible with this plugin"""
        allowed_extensions = ['e01','raw','001','dd','vmdk','zip']
        return evidence['extension'].lower() in allowed_extensions


    def mimetype(self, mimetype):
        """Returns the mimetype of this plugins get command"""
        return "text/plain"

    # TODO Clean and merge with navigate
    # TODO Use mimetypes instead of extensions
    # TODO Add missing extensions
    def get(self, evidence, helper, path_on_disk, request):
        """Returns the result of this plugin to be displayed in a browser"""
        dir_table = []
        file_table = []
        row_evidence_tempalte = Template("""
            <tr>
                <td><img src="/resources/icons/evidence.png" style="width:32px;height:32px;"></td>
                <td><a href="/plugins/fa_directory?{{ url_query }}">{{file_name}}</a></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td>
                    <a href="/plugins/analyze?{{ url_query }}" target="_top" style="padding-right:10px">
                        <span class="fa-stack fa-md">
                            <i class="fa fa-square fa-stack-2x"></i>
                            <i class="fa fa-info-circle fa-stack-1x fa-inverse"></i>
                        </span>
                    </a>
                </td>
            </tr>
        """)
        row_file_template = Template("""
            <tr>
                <!-- {{ file_name }} -->
                <td><img src="/plugins/thumbnail?{{ url_query }}" style="width:32px;height:32px;"></td>
                <td><a href="/plugins/analyze?{{ url_query }}" target="_top">{{file_name}}</a></td>
                <td>{{ mtime }}</td>
                <td>{{ atime }}</td>
                <td>{{ ctime }}</td>
                <td>{{ crtime }}</td>
                <td>{{ size }}</td>
                <td>
                    <a href="/plugins/analyze?{{ url_query }}" target="_top" style="padding-right:10px">
                        <span class="fa-stack fa-md">
                            <i class="fa fa-square fa-stack-2x"></i>
                            <i class="fa fa-info-circle fa-stack-1x fa-inverse"></i>
                        </span>
                    </a>
                    <a href="/plugins/preview?{{ url_query }}&redirect=True" target="_blank" style="padding-right:10px">
                        <span class="fa-stack fa-md">
                            <i class="fa fa-square fa-stack-2x"></i>
                            <i class="fa fa-eye fa-stack-1x fa-inverse"></i>
                        </span>
                    </a>
                    <a href="/plugins/download?{{ url_query }}">
                        <span class="fa-stack fa-md">
                            <i class="fa fa-square fa-stack-2x"></i>
                            <i class="fa fa-download fa-stack-1x fa-inverse"></i>
                        </span>
                    </a>
                </td>
            </tr>
        """)
        row_dir_template = Template("""
            <tr>
                <!-- {{ file_name }} -->
                <td><img src="/plugins/thumbnail?{{ url_query }}" style="width:32px;height:32px;"></td>
                <td><a href="/plugins/fa_directory?{{ url_query }}">{{file_name}}</a></td>
                <td>{{ mtime }}</td>
                <td>{{ atime }}</td>
                <td>{{ ctime }}</td>
                <td>{{ crtime }}</td>
                <td>{{ size }}</td>
                <td>
                    <a href="/plugins/analyze?{{ url_query }}" target="_top" style="padding-right:10px">
                        <span class="fa-stack fa-md">
                            <i class="fa fa-square fa-stack-2x"></i>
                            <i class="fa fa-info-circle fa-stack-1x fa-inverse"></i>
                        </span>
                    </a>
                </td>
            </tr>
        """)


        if evidence['extension'].lower() == 'zip':
            initial_pathspec = [helper.pathspec_helper.get_zip_base_pathspec(evidence['pathspec'])]
        else:
            initial_pathspec = helper.pathspec_helper.get_new_base_pathspecs(evidence['pathspec'])

        if len(initial_pathspec) > 1:
            for item in initial_pathspec:
                dir_table.append(row_evidence_tempalte.render(item))
        else:
            for item in helper.pathspec_helper.list_directory(initial_pathspec[0]['pathspec']):
                if 'file_name' not in item or not item['file_name']:
                    item['file_name'] = '-'
                if item['meta_type'] == 'Directory':
                    dir_table.append(row_dir_template.render(item))
                else:
                    file_table.append(row_file_template.render(item))

        dir_table.sort()
        file_table.sort()

        return '''
            <!DOCTYPE html>
            <html>
            <head>
                    <script src="/resources/jquery-1.11.3.min.js"></script>
                    <script src="/resources/jquery-ui-1.11.4/jquery-ui.min.js" type="text/javascript"></script>
                    <link rel="stylesheet" type="text/css" href="/resources/themes/icon.css">
                    <link rel="stylesheet" type="text/css" href="/resources/themes/jquery.dataTables.min.css">
                    <link rel="stylesheet" href="/resources/font-awesome/css/font-awesome.min.css">
                    <script type="text/javascript" src="/resources/jquery.dataTables.min.js"></script>
                    <script type="text/javascript" class="init">
                        $(document).ready(function() {
                                $('#t01').DataTable({
                                        "paging": false,
                                        "info": false,
                                        "orderClasses": false,
                                        "searching": false
                                        }
                                );
                        } );
                    </script>
            <style>
                table.dataTable thead th {
                    position: relative;
                    background-image: none !important;
                }

                table.dataTable thead th.sorting:after,
                table.dataTable thead th.sorting_asc:after,
                table.dataTable thead th.sorting_desc:after {
                    position: absolute;
                    top: 12px;
                    right: 8px;
                    display: block;
                    font-family: FontAwesome;
                }
                table.dataTable thead th.sorting:after {
                    content: "\\f0dc";
                    color: #ddd;
                    font-size: 0.8em;
                    padding-top: 0.12em;
                }
                table.dataTable thead th.sorting_asc:after {
                    content: "\\f0de";
                }
                table.dataTable thead th.sorting_desc:after {
                    content: "\\f0dd";
                }
                table {
                    overflow-y: scroll;
                    width: 100%;
                }
                table, th, td {
                    border: 0px;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 5px;
                    text-align: left;
                }
                table#t01 tr:nth-child(even) {
                    background-color: #fff;
                }
                table#t01 tr:nth-child(odd) {
                   background-color:#eee;
                }
                table#t01 th {
                    background-color: #444;
                    color: white;
                }
                html{
                    height: 100%;
                }
                body {
                    min-height: 100%;
                    margin: 0px;
                }
                a {
                    text-decoration: none;
                }
                a:link {
                    color: #0c006b;
                }
                a:visited {
                    color: #0c006b;
                }
                a:hover {
                    color: rgb(153, 193, 255);
                }

            </style>
            </head>
                <body>
                   <table id="t01" class="display">
                        <thead>
                        <tr>
                            <th>Icon</th>
                            <th>File Name</th>
                            <th>Modified</th>
                            <th>Accessed</th>
                            <th>Changed</th>
                            <th>Created</th>
                            <th>Size</th>
                            <th>Options</th>
                        </tr>
                        </thead>
                        <tbody>''' \
               + '\n'.join(dir_table) + '\n'.join(file_table) + '</tbody><table>' + \
               '''  </body>
               </html>'''
