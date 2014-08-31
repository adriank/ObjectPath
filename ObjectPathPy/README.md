ObjectPath
==========

The most agile query language for semi-structured data

  #json

How to use it?
--------------
First clone this repo.

```sh
git clone https://github.com/adriank/ObjectPath.git
```
or using PyPi (tends to be outdated!):

```sh
pip install ObjectPath
```

Then import interpreter from core and use it.

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
- <s>clean up the code and fully separate it from AC Runtime project,</s>
- <s>create tools around ObjectPath such as installation helpers,</s>
- <s>build</s> <s>update website</s> <s>prefferably on github.io</s>,
- find people who will give directions on how to extend the language, where it could be useful and so on,
- write a faster implementation of the language (maybe in C?) so that it could handle very large documents and/or many documents in parallel, prefferably asynchronously.
