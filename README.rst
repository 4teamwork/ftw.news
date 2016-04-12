.. contents:: Table of Contents


Introduction
============

ftw.news provides dexterity content types for news articles and an integration
for ftw.simplelayout (news listing block). An optional feature can be installed
allowing the news listing block on the Plone Site to render specially marked
news items only.

Compatibility
-------------

Plone 4.3.x

.. image:: https://jenkins.4teamwork.ch/job/ftw.news-master-test-plone-4.3.x.cfg/badge/icon
   :target: https://jenkins.4teamwork.ch/job/ftw.news-master-test-plone-4.3.x.cfg


Installation
============

- Add the package to your buildout configuration:

::

    [instance]
    eggs +=
        ...
        ftw.news

- Install the "default" GenericSetup profile.

- Optionally (and additionally to the "default" GenericSetup profile) you may
  install the "show-on-homepage" GenericSetup profile.


Usage
=====

Create a news folder then start adding news items into the folder.


Development
===========

**Python:**

1. Fork this repo
2. Clone your fork
3. Shell: ``ln -s development.cfg buildout.cfg``
4. Shell: ``python boostrap.py``
5. Shell: ``bin/buildout``

Run ``bin/test`` to test your changes.

Or start an instance by running ``bin/instance fg``.


Links
=====

- Github: https://github.com/4teamwork/ftw.news
- Issues: https://github.com/4teamwork/ftw.news/issues
- Pypi: http://pypi.python.org/pypi/ftw.news
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.news


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.news`` is licensed under GNU General Public License, version 2.
