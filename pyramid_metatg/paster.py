from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer
import os

class MetaTGProjectTemplate(Template):
    _template_dir = 'paster_template'
    summary = 'pyramid_metatg starter project'
    template_renderer = staticmethod(paste_script_template_renderer)

    def pre(self, command, output_dir, vars): # pragma: no cover
        vars['random_string'] = os.urandom(20).encode('hex')
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

