ObjectPath
==========

The most agile query language for JSON

How to use it?
--------------
First clone Py part of repo. Then import interpreter from core and use it.

Simple example:


`````python
#Being inside ObjectPathPy directory
from core.interpreter import *

myJSON={"x":1,"y":2}
op=Tree(myJSON)
print(op.execute("$.x +$.y"))
`````

For more sophisticated queries check tests/test_ObjectPath.py. All should work perfectly and if not, send bugs via GitHub.

ROADMAP!
------------
- create community!,
- clean up the code and fully separate it from AC Runtime project,
- create tools around ObjectPath such as installation helpers,
- <s>build</s> update website <s>prefferably on github.io</s>,
- find people who will give directions on how to extend the language, where it could be useful and so on,
- write a faster implementation of the language (maybe in C?) so that it could handle very large documents and/or many documents in parallel, prefferably asynchronously. 
