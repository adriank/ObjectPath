#!/bin/sh
pandoc -f markdown -t rst -o README.rst ../README.md
mdTable="aaa Scope aaa Language aaa aaa---aaa---aaa aaa text documents aaa regular
expression aaa aaa XML aaa XPath aaa aaa HTML aaa CSS selectors aaa aaa JSON
documents aaa ObjectPath aaa"
rstTable="==============  ==================
Scope           Language
==============  ==================
text documents  regular expression
XML             XPath
HTML            CSS selectors
JSON documents  ObjectPath
==============  =================="
sed -i "s/\\\|/aaa/g" README.rst
perl -0777 -i.original -pe "s/$mdTable/$rstTable/g" README.rst

python setup.py build
python setup.py sdist bdist_wheel upload
