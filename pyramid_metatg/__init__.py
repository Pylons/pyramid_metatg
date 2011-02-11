import inspect

from zope.interface import Interface
from zope.interface import implements

from pyramid.exceptions import NotFound
from pyramid.path import caller_package
from pyramid.asset import resolve_asset_spec
from pyramid.traversal import traversal_path
from pyramid.renderers import render_to_response
from pyramid.interfaces import ITraverser

def is_exposed(method):
    if inspect.ismethod(method) and hasattr(method, 'decoration'):
        return method.decoration.exposed
    return False

class Decoration(object):
    def __init__(self, template_name=None):
        pkg = caller_package(level=3)
        if template_name:
            _, template_name = resolve_asset_spec(
                template_name, pkg.__name__)
            template_name = '%s:%s' % (_, template_name)
        self.template_name = template_name
        self.exposed = True

    def render(self, context, request, result):
        if self.template_name is None:
            return result
        return render_to_response(self.template_name, result, request=request)

class expose(object):
    def __init__(self, template_name=None):
        self.template_name = template_name

    def __call__(self, wrapped):
        wrapped.decoration = Decoration(self.template_name)
        return wrapped

class IController(Interface):
    pass

class Controller(object):
    implements(IController)

class Traverser(object):
    def __init__(self, root):
        self.root = root

    def __call__(self, request):
        """
        1. Split the PATH_INFO into traversal segments.

        2. The 'current controller' is the root controller.

        2. While there are segments:

           a) Pop the first segment off the traversal stack.  This is the
              'current segment'.

           b) Ask the 'current controller' for an attribute named
              after the current segment.  This becomes the 'next controller'.

           c) If the 'next controller' is not a Controller instance, stop
              traversing and return the 'current controller' as the context.

           d) If the 'next controller' *is* a Controller instance, the
              'next controller' becomes the 'current controller'.  Goto a).

        3.  If we run out of path segments before running out of
            controllers to traverse, return the last controller found
            as the context.

        . """
        path_info = request.path_info
        path = list(traversal_path(path_info))
        traversed = []
        controller = self.root
        controllers = [controller]

        while path:
            segment = path[-1]
            next = getattr(controller, segment, None)
            if next is None or not IController.providedBy(next):
                break
            controller = next
            controllers.append(next)
            traversed.append(segment)
            path.pop(0)

        return dict(
            context=controller,
            view_name='',
            subpath=tuple(path),
            traversed=tuple(traversed),
            virtual_root=self.root,
            virtual_root_path=None,
            controllers=controllers,
            )

def controller_view(context, request):
    controller = context
    remainder = request.subpath

    if hasattr(controller, '_before'):
        controller._before()

    if remainder:
        method_name = remainder[0]
    else:
        method_name = 'index'

    method = getattr(controller, method_name, None)

    if not is_exposed(method):
        for step in reversed(request.controllers):
            method = getattr(step, 'default', None)
            if is_exposed(method):
                break

    if not method:
        raise NotFound(method_name)

    params = request.params.mixed()
    remainder = request.subpath
    response = method(*remainder[1:], **params)

    if hasattr(controller, '_after'):
        controller._after()

    response = method.decoration.render(context, request, response)

    return response

def includeme(config):
    config.registry.registerAdapter(Traverser, (IController,), ITraverser)
    config.add_view(controller_view, context=IController)
    
