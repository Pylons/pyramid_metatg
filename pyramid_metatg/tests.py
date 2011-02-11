import unittest

from pyramid import testing

class TestTraverser(unittest.TestCase):
    def _makeOne(self, root):
        from pyramid_metatg import Traverser
        return Traverser(root)

    def test_path_info_root(self):
        controller = _makeController()
        traverser = self._makeOne(controller)
        result = traverser(testing.DummyRequest(path='/'))
        self.assertEqual(result, {'controllers': [controller],
                                  'view_name': '',
                                  'traversed': (),
                                  'context': controller,
                                  'virtual_root_path': None,
                                  'virtual_root': controller,
                                  'subpath': ()})

    def test_path_info_with_subpath(self):
        controller = _makeController()
        traverser = self._makeOne(controller)
        result = traverser(testing.DummyRequest(path='/foo'))
        self.assertEqual(result, {'controllers': [controller],
                                  'view_name': '',
                                  'traversed': (),
                                  'context': controller,
                                  'virtual_root_path': None,
                                  'virtual_root': controller,
                                  'subpath': ('foo',)})

    def test_path_info_twosteps(self):
        controller = _makeController()
        controller2 = _makeController()
        controller.controller2 = controller2
        traverser = self._makeOne(controller)
        result = traverser(testing.DummyRequest(path='/controller2'))
        self.assertEqual(result, {'controllers': [controller, controller2],
                                  'view_name': '',
                                  'traversed': ('controller2',),
                                  'context': controller2,
                                  'virtual_root_path': None,
                                  'virtual_root': controller,
                                  'subpath': ()})

class TestControllerView(unittest.TestCase):
    def _callFUT(self, context, request):
        from pyramid_metatg import controller_view
        return controller_view(context, request)

    def _makeExposed(self, result):
        class Dummy:
            pass
        def function(self):
            return result
        function.decoration = Dummy()
        function.decoration.exposed = True
        function.decoration.render = lambda *arg: result
        return function

    def test_method_not_found(self):
        from pyramid.exceptions import NotFound
        controller = _makeController()
        request = testing.DummyRequest()
        request.controllers = [controller]
        self.assertRaises(NotFound, self._callFUT, controller, request)

    def test_no_remainder_index_exposed(self):
        import new
        controller = _makeController()
        exposed = self._makeExposed(object)
        controller.index = new.instancemethod(exposed, controller,
                                              controller.__class__)
        request = testing.DummyRequest()
        request.params = DummyParams()
        request.controllers = [controller]
        response = self._callFUT(controller, request)
        self.assertEqual(response, object)

    def test_remainder_index_exposed(self):
        import new
        controller = _makeController()
        exposed = self._makeExposed(object)
        controller.another = new.instancemethod(exposed, controller,
                                                controller.__class__)
        request = testing.DummyRequest()
        request.params = DummyParams()
        request.subpath = ('another',)
        request.controllers = [controller]
        response = self._callFUT(controller, request)
        self.assertEqual(response, object)

    def test_index_not_exposed(self):
        import new
        controller = _makeController()
        exposed = self._makeExposed(object)
        controller.another = None
        controller.default = new.instancemethod(exposed, controller,
                                                controller.__class__)
        request = testing.DummyRequest()
        request.params = DummyParams()
        request.subpath = ('another',)
        request.controllers = [controller]
        response = self._callFUT(controller, request)
        self.assertEqual(response, object)

    def test_before_and_after(self):
        import new
        controller = _makeController()
        exposed = self._makeExposed(object)
        L = []
        controller.index = new.instancemethod(exposed, controller,
                                              controller.__class__)
        controller._before = lambda *arg: L.append('before')
        controller._after = lambda *arg: L.append('after')
        request = testing.DummyRequest()
        request.params = DummyParams()
        request.controllers = [controller]
        self._callFUT(controller, request)
        self.assertEqual(L, ['before', 'after'])

class TestDecoration(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        
    def _makeOne(self, template_name=None):
        from pyramid_metatg import Decoration
        return Decoration(template_name)

    def test_render_with_template_name(self):
        from pyramid.interfaces import IRendererFactory
        renderer = _makeRenderer('123')
        self.config.registry.registerUtility(
            renderer, IRendererFactory, name='.pt')
        decoration = self._makeOne('foo.pt')
        request = testing.DummyRequest()
        response = decoration.render(None, request, None)
        self.assertEqual(response.body, '123')

    def test_render_with_no_template_name(self):
        from pyramid.interfaces import IRendererFactory
        renderer = _makeRenderer('123')
        self.config.registry.registerUtility(
            renderer, IRendererFactory, name='.pt')
        decoration = self._makeOne()
        request = testing.DummyRequest()
        response = decoration.render(None, request, '123')
        self.assertEqual(response, '123')

class TestExpose(unittest.TestCase):
    def _makeOne(self, template_name=None):
        from pyramid_metatg import expose
        return expose(template_name)

    def test_it(self):
        class Dummy(object):
            pass
        ob = Dummy()
        decorator = self._makeOne('foo.pt')
        result = decorator(ob)
        self.failUnless(result is ob)
        self.assertEqual(result.decoration.template_name,
                         'pyramid_metatg:foo.pt')

class Test_includeme(unittest.TestCase):
    def _callFUT(self, config):
        from pyramid_metatg import includeme
        includeme(config)

    def test_it(self):
        from pyramid.config import Configurator
        from pyramid_metatg import includeme
        from pyramid.interfaces import IViewClassifier
        from pyramid.interfaces import IView
        from pyramid.interfaces import ITraverser
        from pyramid.interfaces import IRequest
        from pyramid_metatg import IController
        from pyramid_metatg import controller_view
        from pyramid_metatg import Controller
        from pyramid_metatg import Traverser

        config = Configurator(autocommit=True)

        # did it add the view?
        self._callFUT(config)
        includeme(config)
        view = config.registry.adapters.lookup(
            (IViewClassifier, IRequest, IController),
            IView, default=None)
        self.assertEqual(view, controller_view)

        # did it register the traverser?
        controller = Controller()
        traverser = config.registry.queryAdapter(controller, ITraverser)
        self.assertEqual(traverser.__class__, Traverser)
        

def _makeRenderer(result):
    class DummyRenderer(object):
        def __init__(self, path):
            self.path = path

        def __call__(self, response, d):
            return result
    return DummyRenderer

def _makeController():
    from pyramid_metatg import IController
    from zope.interface import implements
    class DummyController(object):
        implements(IController)
    return DummyController()

class DummyParams(dict):
    def mixed(self):
        return self
    
