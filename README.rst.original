ObjectPath
==========

|Downloads| |Build Status| |Code Health| |Coverage Status|

The agile NoSQL query language for semi-structured data
-------------------------------------------------------

**#Python #NoSQL #Javascript #JSON #nested-array-object**

ObjectPath is a query language similar to XPath or JSONPath, but much
more powerful thanks to embedded arithmetic calculations, comparison
mechanisms and built-in functions. This makes the language more like SQL
in terms of expressiveness, but it works over JSON documents rather than
relations. ObjectPath can be considered a full-featured expression
language. Besides selector mechanism there is also boolean logic, type
system and string concatenation available. On top of that, the language
implementations (Python at the moment; Javascript is in beta!) are
secure and relatively fast.

More at `ObjectPath site <http://objectpath.org/>`__

.. figure:: http://adriank.github.io/ObjectPath/img/op-colors.png
   :alt: ObjectPath img

   ObjectPath img

ObjectPath makes it easy to find data in big nested JSON documents. It
borrows the best parts from E4X, JSONPath, XPath and SQL. ObjectPath is
to JSON documents what XPath is to XML. Other examples to ilustrate this
kind of relationship are:

============== ==================
Scope          Language
============== ==================
text documents regular expression
XML            XPath
HTML           CSS selectors
JSON documents ObjectPath
============== ==================

Documentation
-------------

`ObjectPath Reference <http://objectpath.org/reference.html>`__

Command line usage
------------------

.. code:: sh

   $ sudo pip install objectpath
   $ objectpath file.json

or

.. code:: sh

   $ git clone https://github.com/adriank/ObjectPath.git
   $ cd ObjectPath
   $ python shell.py file.json

Python usage
------------

.. code:: sh

   $ sudo pip install objectpath
   $ python
   >>> from objectpath import *
   >>> tree=Tree({"a":1})
   >>> tree.execute("$.a")
   1
   >>>

.. code:: sh

   $ git clone https://github.com/adriank/ObjectPath.git
   $ cd ObjectPath
   $ python
   >>> from objectpath import *
   >>> tree=Tree({"a":1})
   >>> tree.execute("$.a")
   1
   >>>

Contributing & bugs
-------------------

I appreciate all contributions and bugfix requests for ObjectPath,
however since I don’t code in Python any more, this library is not
maintained as of now. Since I can’t fully assure that code contributed
by others meets quality standards, I can’t accept PRs.

If you feel you could maintain this code, ping me. I’d be more than
happy to transfer this repo to a dedicated ObjectPath organization on
GitHub and give the ownership to someone with more time for this project
than me.

License
-------

**MIT**

.. |Downloads| image:: https://img.shields.io/pypi/dm/objectpath.svg
   :target: https://pypi.python.org/pypi/objectpath/
.. |Build Status| image:: https://travis-ci.org/adriank/ObjectPath.svg?branch=master
   :target: https://travis-ci.org/adriank/ObjectPath
.. |Code Health| image:: https://landscape.io/github/adriank/ObjectPath/master/landscape.png
   :target: https://landscape.io/github/adriank/ObjectPath/master
.. |Coverage Status| image:: https://coveralls.io/repos/adriank/ObjectPath/badge.png?branch=master
   :target: https://coveralls.io/r/adriank/ObjectPath?branch=master
