TurboGears-like object dispatch for Pyramid
===========================================

This package provides an example of how someone might create TurboGears-like
object dispatch for Pyramid.

TurboGears uses a model whereby a tree of "controllers" is traversed and
subsequently one of the methods of the "final" traversed controller is called
to return a response.  This differs from default Pyramid behavior inasmuch as
the objects traversed by the default Pyramid traverser ("resources") are not
assumed to have response-generating logic as methods.  Instead, under the
default Pyramid traversal regime, after a "context" resource is found a
"view" is found by introspecting the type of the context resource and
matching it against a separate registry of view functions / methods /
instances.  TurboGears conflates these two steps, so in order to emulate
TG-style object dispatch, the Pyramid traverser is replaced with one that
returns a controller and a default view is registered against all Controller
objects; this default view finds the "right" method of the returned
controller to use to generate a response and calls it.

This package provides an alternate traverser, a view implementation that is
used for all Controller objects resulting from traversal , and a paster
template that allows you to try out the result from end-to-end.

Trying it out
-------------

1.  ``python setup.py install``

2.  ``paster create -t pyramid_metatg myproject``

3.  ``cd myproject``

4.  ``python setup.py develop``

5.  ``paster serve development.ini``

Visit the browser on 6543.
