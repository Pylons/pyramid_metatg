TurboGears-like object dispatch for Pyramid
===========================================

This package provides TurboGears-like object dispatch for Pyramid.
TurboGears uses a model whereby "controllers" are traversed and called to
return a response.  This differs from the default Pyramid traverser inasmuch
that the objects that the default traverser traverses are assumed never to be
callable (all response generation is done in a view).

This package provides an alternate traverser, a view implementation
that is used for *all* objects resulting from traversal , and a paster
template that allows you to try out the result from end-to-end.

Trying it out
-------------

1.  ``python setup.py install``

2.  ``paster create -t pyramid_metatg myproject``

3.  ``cd myproject``

4.  ``python setup.py develop``

5.  ``paster serve myproject.ini``

Visit the browser on 6543.
