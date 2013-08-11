ObjectPath
==========

The most agile NoSQL query language for JSON
-----------------------------------------------

ObjectPath is a query language similar to XPath or JSONPath, but much more powerful thanks to embedded arithmetic calculations, comparison mechanisms and built-in functions. This makes the language more like SQL in terms of expressiveness, but it works over JSON documents rather than relations. ObjectPath can be considered a full-featured expression language. Besides selector mechanism there is also boolean logic, type system and string concatenation available. On top of that, the language implementations (Python at the moment; Javascript is in beta!) are secure and relatively fast.

More at [ObjectPath site](http://adriank.github.io/ObjectPath)

ObjectPath makes it easy to find data in big nested JSON documents. It borrows the best parts from E4X, JSONPath, XPath and SQL. ObjectPath is to JSON documents what XPath is to XML. Other examples to ilustrate this kind of relationship are:

<table>
    <thead>
       <th>Scope</th>
       <th>Language</th>
    </thead>
    <tr>
       <td>text documents</td>
       <td>regular expression</td>
    </tr>
    <tr>
       <td>XML</td>
       <td>XPath</td>
    </tr>
    <tr>
       <td>HTML</td>
       <td>CSS selectors</td>
    </tr>
    <tr>
       <td>JSON documents</td>
       <td>ObjectPath</td>
    </tr>
</table>

Tags
----

NoSQL, MongoDB, programming language independent, like XPath/regex/CSS selectors, supported, evolving

Documentation
-------------

[ObjectPath Reference](http://docs.asyncode.com/text/ObjectPath-reference)

What's in this repo?
--------------------

ObjectPathPY - Python implementation of ObjectPath. This is a stable piece of code extracted from AC Runtime used in production for over one year without problems. While ObjectPath paths are working perfectly (all tests are passed), integration with Python programs is not documented. Use ObjectPath.py file as a reference of usage. Also Python-specific topics such as generators, chains and optimizations are not documented (comming soon!).

ObjectPathJS - beta version of Javascript implementation. Many tests passed, {} and functions are not implemented yet. Javascript implementation has the very same API as the Python version.
