from setuptools import setup, find_packages
import os

version = '1.16.1'
maintainer = 'Mathias Leimgruber'

tests_require = [
    'ftw.builder',
    'ftw.chameleon',
    'ftw.news[mopage_publisher_receiver]',
    'ftw.referencewidget[tests]',
    'ftw.subsite',
    'ftw.testbrowser',
    'ftw.testing>=1.11.0',
    'path.py',
    'plone.app.testing',
    'plone.testing',
    'plone.app.contenttypes',
    'plone.restapi',
]

extras_require = {
    'tests': tests_require,
    'test': tests_require,

    # The mopage_publisher_receiver should be installed on a ftw.publisher
    # receiver installation in order to enable the mopage trigger function.
    # It should *NOT* be installed on ftw.pubsliher.sender site, since
    # the trigger will then be triggered too early.
    'mopage_publisher_receiver': [
        'collective.taskqueue',
        'ftw.publisher.receiver',
        'requests',
        'ftw.simplelayout >= 1.15.0',
    ],
    'restapi': [
        'plone.restapi'
    ]
}

setup(
    name='ftw.news',
    version=version,
    description='Provides dexterity content types for news articles.',
    long_description=open('README.rst').read() + '\n' + open(
        os.path.join('docs', 'HISTORY.txt')).read(),

    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.1',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw news',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    maintainer=maintainer,
    url='https://github.com/4teamwork/ftw.news',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw', ],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'Plone',
        'ftw.autofeature',
        'ftw.datepicker',
        'ftw.keywordwidget',
        'ftw.referencewidget',
        'ftw.simplelayout [contenttypes]',
        'plone.api',
        'plone.dexterity',
        'plone.directives.form',
        'ftw.upgrade',
        'setuptools',
    ],

    tests_require=tests_require,
    extras_require=extras_require,

    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
