import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

setup(name='pyramid_metatg',
      version='0.0',
      description="TurboGears2-like object dispatch for Pyramid (example)",
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
      keywords='pyramid pylons turbogears tg2',
      author='Chris McDonough',
      author_email='chrism@plope.com',
      url='http://pylonsproject.org',
      license='BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = ['pyramid'],
      tests_require = ['pyramid'],
      test_suite="pyramid_metatg.tests",
      entry_points = """\
        [paste.paster_create_template]
        pyramid_metatg=pyramid_metatg.paster:MetaTGProjectTemplate
      """,
      )
