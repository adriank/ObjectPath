ObjectPath
==========

[![Build Status](https://travis-ci.org/adriank/ObjectPath.svg?branch=master)](https://travis-ci.org/adriank/ObjectPath)
[![Code Health](https://landscape.io/github/adriank/ObjectPath/master/landscape.png)](https://landscape.io/github/adriank/ObjectPath/master)
[![Coverage Status](https://coveralls.io/repos/adriank/ObjectPath/badge.png?branch=master)](https://coveralls.io/r/adriank/ObjectPath?branch=master)

The agile NoSQL query language for semi-structured data
-----------------------------------------------

**#Python #NoSQL #Javascript #JSON #XML #nested-array-object**

ObjectPath is a query language similar to XPath or JSONPath, but much more powerful thanks to embedded arithmetic calculations, comparison mechanisms and built-in functions. This makes the language more like SQL in terms of expressiveness, but it works over JSON documents rather than relations. ObjectPath can be considered a full-featured expression language. Besides selector mechanism there is also boolean logic, type system and string concatenation available. On top of that, the language implementations (Python at the moment; Javascript is in beta!) are secure and relatively fast.

More at [ObjectPath site](http://adriank.github.io/ObjectPath)

![ObjectPath img](http://adriank.github.io/ObjectPath/img/op-colors.png)

ObjectPath makes it easy to find data in big nested JSON documents. It borrows the best parts from E4X, JSONPath, XPath and SQL. ObjectPath is to JSON documents what XPath is to XML. Other examples to ilustrate this kind of relationship are:

| Scope  | Language |
|---|---|
| text documents  | regular expression  |
| XML  | XPath  |
| HTML  | CSS selectors  |
| JSON documents | ObjectPath |


Documentation
-------------

[ObjectPath Reference](http://adriank.github.io/ObjectPath/reference.html)

What's in this repo?
--------------------

ObjectPathPY - Python implementation of ObjectPath, used in production for over two years without problems. Use objectpath.py file as a example of usage.

ObjectPathJS - beta version of Javascript implementation. Many tests passed, {} and functions are not implemented yet. Javascript implementation has the very same API as the Python version.

Command line usage
-----

`````sh
$ sudo pip install objectpath
$ objectpath file.json
`````

`````sh
$ git clone https://github.com/adriank/ObjectPath.git
$ cd ObjectPath/ObjectPathPy
$ python objectpath file.json
`````

Python usage
----------------

`````sh
$ sudo pip install objectpath
$ python
>>> from objectpath import *
>>> tree=Tree({"a":1})
>>> tree.execute("$.a")
1
>>>
`````

`````sh
$ git clone https://github.com/adriank/ObjectPath.git
$ python
>>> from objectpath import *
>>> tree=Tree({"a":1})
>>> tree.execute("$.a")
1
>>>
`````

License
-------

AGPLv3
