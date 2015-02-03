ObjectPath
==========

[![Downloads](https://pypip.in/download/objectpath/badge.svg)](https://pypi.python.org/pypi/objectpath/)
[![License](https://pypip.in/license/objectpath/badge.svg)](https://pypi.python.org/pypi/objectpath/)
[![Build Status](https://travis-ci.org/adriank/ObjectPath.svg?branch=master)](https://travis-ci.org/adriank/ObjectPath)
[![Code Health](https://landscape.io/github/adriank/ObjectPath/master/landscape.png)](https://landscape.io/github/adriank/ObjectPath/master)
[![Coverage Status](https://coveralls.io/repos/adriank/ObjectPath/badge.png?branch=master)](https://coveralls.io/r/adriank/ObjectPath?branch=master)


The agile NoSQL query language for semi-structured data
-----------------------------------------------

**#Python #NoSQL #Javascript #JSON #nested-array-object**

ObjectPath is a query language similar to XPath or JSONPath, but much more powerful thanks to embedded arithmetic calculations, comparison mechanisms and built-in functions. This makes the language more like SQL in terms of expressiveness, but it works over JSON documents rather than relations. ObjectPath can be considered a full-featured expression language. Besides selector mechanism there is also boolean logic, type system and string concatenation available. On top of that, the language implementations (Python at the moment; Javascript is in beta!) are secure and relatively fast.

More at [ObjectPath site](http://objectpath.org/)

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

[ObjectPath Reference](http://objectpath.org/reference.html)

Command line usage
-----

`````sh
$ sudo pip install objectpath
$ objectpath file.json
`````
or
`````sh
$ git clone https://github.com/adriank/ObjectPath.git
$ cd ObjectPath
$ python shell.py file.json
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
$ cd ObjectPath
$ python
>>> from objectpath import *
>>> tree=Tree({"a":1})
>>> tree.execute("$.a")
1
>>>
`````

License
-------

**AGPLv3**

Using ObjectPath language in your project does not mean that your project is a derivative work, provided that you don't
- extend the language functionality,
- make optimizations,
- sub-class any of it's modules.

AGPL v3 license has been chosen to ensure language consistency and provide a way to finance its development.

**If AGPL v3 is too restrictive for you, please consider buying a commercial licenses provided by Asyncode. This is the preferred way of supporting this project financially.**
