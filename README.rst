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


Mopage Support
--------------

``ftw.news`` provides integration for the mopage mobile app
(http://web.anthrazit.org/).


Data Endpoint
~~~~~~~~~~~~~

The view ``mopage.news.xml`` returns an XML-feed with the latest news within
the context it is called. It can becalled on any type of object.

- The mopage-API expects a ``partnerid`` and a ``importid``.
  They are incldued when submitted via GET-parameter, e.g.:
  ``http://foo.com/news/mopage.news.xml?partnerid=123&importid=456``

- The endpoint returns only 100 news by default.
  This can be changed with the parameter ``?per_page=200``.

- The endpoint returns ``Link``-headers in the response with pagination links.


Trigger behavior
~~~~~~~~~~~~~~~~

The behavior ``ftw.news.behaviors.mopage.IPublisherMopageTrigger`` can be added
on a news folder in order to configure automatic notification to the mopage API
that new news are published.

In order for the behavior to work properly you need an ``ftw.publisher`` setup.
Only the receiver-side (public website) will trigger the notification.
A configured ``collective.taskqueue`` is required for this to work.

Buildout example:

.. code:: ini

    [instance]
    eggs +=
        ftw.news[mopage_publisher_receiver]

    zope-conf-additional +=
        %import collective.taskqueue
        <taskqueue />
        <taskqueue-server />


Then enable the behavior for the news container type and configure the trigger
with the newly availabe fields.



Development
==========

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
