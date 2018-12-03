#!/usr/bin/env python
# -*- coding: utf-8 -*-

from objectpath.core.interpreter import *
from objectpath.core import ProgrammingError, ExecutionError
from random import randint, choice
#from bson.objectid import ObjectId
import sys, unittest, os

sys.setrecursionlimit(20000)

object1 = {
  "__lang__": "en",
  "test": {
    "_id": 1,
    "name": "aaa",
    "o": {
      "_id": 2
    },
    "l": [{
      "_id": 3,
      "aaa": "ddd",
      "false": 2
    }, {
      "_id": 4
    }]
  }
}

object2 = {
  "store": {
    "book": [{
      "id":1,
      "category": "reference",
      "author": "Nigel Rees",
      "title": "Sayings of the Century",
      "price": 8.95
    },
    {
      "category": "fiction",
      "author": "Evelyn Waugh",
      "title": "Sword of Honour",
      "price": 12.99
    },
    {
      "category": "fiction",
      "author": "Herman Melville",
      "title": "Moby Dick",
      "isbn": "0-553-21311-3",
      "price": 8.99
    },
    {
      "category": "fiction",
      "author": "J. R. R. Tolkien",
      "title": "The Lord of the Rings",
      "isbn": "0-395-19395-8",
      "price": 22.99
    }],
    "bicycle": {
      "color": "red",
      "price": 19.95
    },
    "k": [{
      "_id": 4
    }]
  }
}

object3 = {
  "item_1": {
    "value": "foo",
    "x": 5.6,
    "y": 9
  },
  "item_2": {
    "value": "bar",
    "x": 5.6,
    "y": 9.891
  },
  "item_3": {
    "value": "foobar",
    "x": 5.6,
    "y": 9.8
  }
}

object4 = {
  "root": {
    "response": {
      "200": {
        "value": 5,
      },
      "201": {
        "value": 4,
      },
      "404": {
        "value": 0,
      }
    }
  }
}

tree1 = Tree(object1)
tree2 = Tree(object2)
tree3 = Tree(object3)
tree4 = Tree(object4)

def execute_raw(expr):
  return tree1.execute(expr)

TYPES = [generator, chain]
if sys.version_info.major > 2:
  TYPES += [map]

TYPES = tuple(TYPES)

def execute(expr):
  r = tree1.execute(expr)
  if isinstance(r, TYPES):
    return list(r)
  else:
    return r

def execute2(expr):
  r = tree2.execute(expr)
  if isinstance(r, TYPES):
    return list(r)
  else:
    return r

def execute3(expr):
  r = tree3.execute(expr)
  if isinstance(r, TYPES):
    return list(r)
  else:
    return r

def execute4(expr):
  r = tree4.execute(expr)
  if isinstance(r, TYPES):
    return list(r)
  else:
    return r

class ObjectPath(unittest.TestCase):

  def test_simple_types(self):
    self.assertEqual(execute("null"), None)
    self.assertEqual(execute("true"), True)
    self.assertEqual(execute("false"), False)
    self.assertEqual(execute("''"), "")
    self.assertEqual(execute('""'), "")
    self.assertEqual(execute("2"), 2)
    self.assertEqual(execute("2.0"), 2.0)

  def test_arrays(self):
    self.assertEqual(execute("[]"), [])
    self.assertEqual(list(execute("[1,2,3]")), [1, 2, 3])
    self.assertEqual(
      list(execute("[false,null,true,'',\"\",2,2.0,{}]")),
      [False, None, True, '', "", 2, 2.0, {}]
    )

  def test_objects(self):
    self.assertEqual(execute("{}"), {})
    self.assertEqual(
      execute("{a:1,b:false,c:'string'}"), {
        "a": 1,
        "b": False,
        "c": 'string'
      }
    )
    self.assertEqual(
      execute("{'a':1,'b':false,'c':'string'}"), {
        "a": 1,
        "b": False,
        "c": 'string'
      }
    )

  def test_arithm_add(self):
    self.assertEqual(execute("2+3"), 5)
    self.assertEqual(execute("2+3+4"), 9)
    self.assertEqual(execute("++3"), 3)
    # null is treated as neutral value
    self.assertEqual(execute("null+3"), 3)
    self.assertEqual(execute("3+null"), 3)

  def test_arithm_sub(self):
    self.assertEqual(execute("-1"), -1)
    self.assertEqual(execute("2-3"), 2 - 3)
    self.assertEqual(execute("2.2-3.4"), 2.2 - 3.4)
    self.assertEqual(execute("-+-3"), 3)
    self.assertEqual(execute("+-+3"), -3)

  def test_arithm_mul(self):
    self.assertEqual(execute("2*3*5*6"), 180)

  def test_arithm_mod(self):
    self.assertEqual(execute("2%3"), 2.0 % 3)
    self.assertEqual(execute("2.0%3"), 2.0 % 3)
    self.assertEqual(execute("float(2)%3"), float(2) % 3)

  def test_arithm_div(self):
    self.assertEqual(execute("2/3"), 2.0/3)
    self.assertEqual(execute("2.0/3"), 2.0/3)
    self.assertEqual(execute("float(2)/3"), float(2)/3)

  def test_arithm_group(self):
    self.assertEqual(execute("2-3+4+5-7"), 2 - 3 + 4 + 5 - 7)
    self.assertEqual(execute("33*2/5-2"), 33*2/5.0 - 2)
    self.assertEqual(execute("33-4*5+2/6"), 33 - 4*5 + 2/6.0)
    #self.assertEqual(execute("2//3//4//5"), ('//', ('//', ('//', 2, 3), 4), 5))

  def test_arithm_parentheses(self):
    self.assertEqual(execute("+6"), 6)
    self.assertEqual(execute("2+2*2"), 6)
    self.assertEqual(execute("2+(2*2)"), 6)
    self.assertEqual(execute("(2+2)*2"), 8)
    self.assertEqual(execute("(33-4)*5+2/6"), (33 - 4)*5 + 2/6.0)
    self.assertEqual(execute("2/3/(4/5)*6"), 2/3.0/(4/5.0)*6)
    self.assertEqual(execute("((2+4))+6"), ((2 + 4)) + 6)

  def test_logic_negatives(self):
    self.assertEqual(execute("not false"), True)
    self.assertEqual(execute("not null"), True)
    self.assertEqual(execute("not 0"), True)
    self.assertEqual(execute("not 0.0"), True)
    self.assertEqual(execute("not ''"), True)
    self.assertEqual(execute("not []"), True)
    self.assertEqual(execute("not {}"), True)

  def test_logic_not(self):
    self.assertEqual(execute("not false"), True)
    self.assertEqual(execute("not not not false"), True)

  def test_logic_or(self):
    self.assertEqual(execute("1 or 2"), 1)
    self.assertEqual(execute("0 or 2"), 2)
    self.assertEqual(execute("'a' or 0 or 3"), 'a')
    self.assertEqual(
      execute("null or false or 0 or 0.0 or '' or [] or {}"), {}
    )

  def test_logic_and(self):
    self.assertEqual(execute("1 and 2"), 2)
    self.assertEqual(execute("0 and 2"), 0)
    self.assertEqual(execute("'a' and false and 3"), False)
    self.assertEqual(
      execute("true and 1 and 1.0 and 'foo' and [1] and {a:1}"), {"a": 1}
    )

  def test_comparison_regex(self):
    self.assertIsInstance(execute("/aaa/"), type(re.compile("")))
    self.assertEqual(execute("/.*aaa/ matches 'xxxaaaadddd'"), True)
    self.assertEqual(execute("'.*aaa' matches 'xxxaaaadddd'"), True)
    self.assertEqual(execute("'.*aaa' matches ['xxxaaaadddd', 'xxx']"), True)

  def test_comparison_is(self):
    self.assertEqual(execute("2 is 2"), True)
    self.assertEqual(execute("'2' is 2"), True)
    self.assertEqual(execute("2 is '2'"), True)
    self.assertEqual(execute("2 is 2.0"), True)
    self.assertEqual(execute("0.1+0.2 is 0.3"), True)
    self.assertEqual(execute("[] is []"), True)
    self.assertEqual(execute("[1] is [1]"), True)
    self.assertEqual(execute("{} is {}"), True)
    self.assertEqual(execute("{} is []"), False)
    self.assertEqual(execute("None is 'aaa'"), False)
    self.assertEqual(execute("None is None"), True)
    self.assertEqual(execute("{'aaa':1} is {'aaa':1}"), True)
    #oid=ObjectId()
    #self.assertEqual(execute("ObjectID('"+str(oid)+"') is '"+str(oid)+"'"), True)

  def test_comparison_isnot(self):
    self.assertEqual(execute("None is not None"), False)
    self.assertEqual(execute("None is not 'aaa'"), True)
    self.assertEqual(execute("{} is not []"), True)
    self.assertEqual(execute("3 is not 6"), True)
    self.assertEqual(execute("3 is not '3'"), False)
    self.assertEqual(execute("[] is not [1]"), True)
    self.assertEqual(execute("[] is not []"), False)
    self.assertEqual(execute("{'aaa':2} is not {'bbb':2}"), True)
    self.assertEqual(execute("{} is not {}"), False)

  def test_membership_in(self):
    self.assertEqual(execute("4 in [6,4,3]"), True)
    self.assertEqual(execute("4 in {4:true}"), True)
    self.assertEqual(execute("[2,3] in [6,4,3]"), True)

  def test_membership_notin(self):
    self.assertEqual(execute("4 not in []"), True)
    self.assertEqual(execute("1 not in {'232':2}"), True)
    self.assertEqual(execute("[2,5] not in [6,4,3]"), True)

  def test_complex(self):
    self.assertEqual(execute("23 is not 56 or 25 is 57"), True)
    self.assertEqual(execute("2+3/4-6*7>0 or 10 is not 11 and 14"), 14)

  def test_comparison_lt(self):
    self.assertEqual(execute("2<3"), True)
    self.assertEqual(execute("3<3"), False)
    self.assertEqual(execute("2<=2"), True)
    self.assertEqual(execute("2<=1"), False)

  def test_comparison_gt(self):
    self.assertEqual(execute("5>4"), True)
    self.assertEqual(execute("5>5"), False)
    self.assertEqual(execute("5>=5"), True)

  def test_concatenation(self):
    self.assertEqual(execute("'a'+'b'+\"c\""), 'abc')
    self.assertEqual(execute("'5'+5"), '55')
    self.assertEqual(execute("5+'5'"), 10)
    self.assertEqual(list(execute("[1,2,4] + [3,5]")), [1, 2, 4, 3, 5])
    self.assertEqual(
      execute('{"a":1,"b":2} + {"a":2,"c":3}'), {
        "a": 2,
        "b": 2,
        "c": 3
      }
    )
    self.assertRaises(
      ProgrammingError, lambda: execute('{"a":1,"b":2} + "sss"')
    )

  def test_builtin_casting(self):
    self.assertEqual(execute("str('foo')"), 'foo')
    self.assertEqual(execute("str(1)"), '1')
    self.assertEqual(execute("str(1.0)"), '1.0')
    self.assertEqual(execute("str(1 is 1)"), 'true')
    self.assertEqual(execute("int(1)"), 1)
    self.assertEqual(execute("int(1.0)"), 1)
    self.assertEqual(execute("int('1')"), 1)
    #Python can't handle that
    #self.assertEqual(execute("int('1.0')"), 1)
    self.assertEqual(execute("float(1.0)"), 1.0)
    self.assertEqual(execute("float(1)"), 1.0)
    self.assertEqual(execute("float('1')"), 1.0)
    self.assertEqual(execute("float('1.0')"), 1.0)
    self.assertEqual(execute("array()"), [])
    self.assertEqual(execute("array([])"), [])
    self.assertEqual(execute("array('abc')"), ['a', 'b', 'c'])
    self.assertEqual(
      execute("array(dateTime([2011,4,8,12,0]))"), [2011, 4, 8, 12, 0, 0, 0]
    )
    self.assertEqual(execute("array(date([2011,4,8]))"), [2011, 4, 8])
    self.assertEqual(execute("array(time([12,12,30]))"), [12, 12, 30, 0])

  def test_builtin_arithmetic(self):
    self.assertEqual(execute("sum([1,2,3,4])"), sum([1, 2, 3, 4]))
    self.assertEqual(execute("sum([2,3,4,'333',[]])"), 9)
    self.assertEqual(execute("sum(1)"), 1)
    self.assertEqual(execute("min([1,2,3,4])"), min([1, 2, 3, 4]))
    self.assertEqual(execute("min([2,3,4,'333',[]])"), 2)
    self.assertEqual(execute("min(1)"), 1)
    self.assertEqual(execute("max([1,2,3,4])"), max([1, 2, 3, 4]))
    self.assertEqual(execute("max([2,3,4,'333',[]])"), 4)
    self.assertEqual(execute("max(1)"), 1)
    self.assertEqual(execute("avg([1,2,3,4])"), 2.5)
    self.assertEqual(execute("avg([1,3,3,1])"), 2.0)
    self.assertEqual(execute("avg([1.1,1.3,1.3,1.1])"), 1.2000000000000002)
    self.assertEqual(execute("avg([2,3,4,'333',[]])"), 3)
    self.assertEqual(execute("avg(1)"), 1)
    self.assertEqual(execute("round(2/3)"), round(2.0/3))
    self.assertEqual(execute("round(2/3,3)"), round(2.0/3, 3))
    # edge cases
    self.assertEqual(execute("avg(1)"), 1)
    # should ommit 'sss'
    self.assertEqual(execute("avg([1,'sss',3,3,1])"), 2.0)

  def test_builtin_string(self):
    self.assertEqual(execute("replace('foobar','oob','baz')"), 'fbazar')
    self.assertEqual(execute("""escape('&lt;')"""), "&amp;lt;")
    self.assertEqual(execute("""escape('<"&>')"""), "&lt;&quot;&amp;&gt;")
    self.assertEqual(execute("""unescape('&lt;&quot;&amp;&gt;')"""), "<\"&>")
    self.assertEqual(execute("upper('aaa')"), "AAA")
    self.assertEqual(execute("lower('AAA')"), "aaa")
    self.assertEqual(execute("title('AAA aaa')"), "Aaa Aaa")
    self.assertEqual(execute("capitalize('AAA Aaa')"), "Aaa aaa")
    self.assertEqual(execute("split('aaa aaa')"), ["aaa", "aaa"])
    self.assertEqual(execute("split('aaaxaaa','x')"), ["aaa", "aaa"])
    self.assertEqual(execute("join(['aaą','aaę'],'ć')"), "aaąćaaę")
    self.assertEqual(execute("join(['aaa','aaa'])"), "aaaaaa")
    self.assertEqual(execute("join(['aaa','aaa',3,55])"), "aaaaaa355")
    self.assertEqual(execute('slice("Hello world!", [6, 11])'), "world")
    self.assertEqual(execute('slice("Hello world!", [6, -1])'), "world")
    self.assertEqual(
      execute('slice("Hello world!", [[0,5], [6, 11]])'), ["Hello", "world"]
    )
    self.assertRaises(ProgrammingError, lambda: execute('slice()'))
    self.assertRaises(ExecutionError, lambda: execute('slice("", {})'))
    self.assertEqual(execute('map(upper, ["a", "b", "c"])'), ["A", "B", "C"])

  def test_builtin_arrays(self):
    self.assertEqual(execute("sort([1,2,3,4]+[2,4])"), [1, 2, 2, 3, 4, 4])
    self.assertEqual(execute("sort($.._id)"), [1, 2, 3, 4])
    self.assertEqual(
      execute("sort($..l.*, _id)"), [{
        '_id': 3,
        'aaa': 'ddd',
        'false': 2
      }, {
        '_id': 4
      }]
    )
    self.assertEqual(execute("reverse([1,2,3,4]+[2,4])"), [4, 2, 4, 3, 2, 1])
    self.assertEqual(execute("reverse(sort($.._id))"), [4, 3, 2, 1])
    self.assertEqual(execute("len([1,2,3,4]+[2,4])"), 6)
    self.assertEqual(execute("unique([1,1,3,3])"), [1, 3])
    # edge cases
    self.assertEqual(execute("len(True)"), True)
    self.assertEqual(execute("len('aaa')"), 3)

  def test_builtin_time(self):
    import datetime
    self.assertIsInstance(execute("now()"), datetime.datetime)
    self.assertIsInstance(execute("date()"), datetime.date)
    self.assertIsInstance(execute("date(now())"), datetime.date)
    self.assertIsInstance(execute("date([2001,12,30])"), datetime.date)
    self.assertIsInstance(execute("time()"), datetime.time)
    self.assertIsInstance(execute("time(now())"), datetime.time)
    self.assertIsInstance(execute("time([12,23])"), datetime.time)
    self.assertIsInstance(execute("time([12,23,21,777777])"), datetime.time)
    self.assertIsInstance(execute("dateTime(now())"), datetime.datetime)
    self.assertIsInstance(
      execute("dateTime([2001,12,30,12,23])"), datetime.datetime
    )
    self.assertIsInstance(
      execute("dateTime([2001,12,30,12,23,21,777777])"), datetime.datetime
    )
    self.assertIsInstance(execute('dateTime("1980-05-11 04:22:33", "%Y-%m-%d %H:%M:%S")'), datetime.datetime)
    self.assertEqual(str(execute('dateTime("1980-05-11 04:22:33", "%Y-%m-%d %H:%M:%S")')), "1980-05-11 04:22:33")

    self.assertEqual(
      execute("toMillis(dateTime([2001,12,30,12,23,21,777777]))"),
      1009715001777
    )
    self.assertIsInstance(
      execute("dateTime(date(),time())"), datetime.datetime
    )
    self.assertIsInstance(
      execute("dateTime(date(),[12,23])"), datetime.datetime
    )
    self.assertIsInstance(
      execute("dateTime(date(),[12,23,21,777777])"), datetime.datetime
    )
    self.assertIsInstance(
      execute("dateTime([2001,12,30],time())"), datetime.datetime
    )
    self.assertEqual(
      execute("array(time([12,30])-time([8,00]))"), [4, 30, 0, 0]
    )
    self.assertEqual(
      execute("array(time([12,12,12,12])-time([8,8,8,8]))"), [4, 4, 4, 4]
    )
    self.assertEqual(
      execute("array(time([12,12,12,12])-time([1,2,3,4]))"), [11, 10, 9, 8]
    )
    self.assertEqual(
      execute("array(time([12,00])-time([1,10]))"), [10, 50, 0, 0]
    )
    self.assertEqual(
      execute("array(time([1,00])-time([1,10]))"), [23, 50, 0, 0]
    )
    self.assertEqual(
      execute("array(time([0,00])-time([0,0,0,1]))"), [23, 59, 59, 999999]
    )
    self.assertEqual(
      execute("array(time([0,0])+time([1,1,1,1]))"), [1, 1, 1, 1]
    )
    self.assertEqual(
      execute("array(time([0,0])+time([1,2,3,4]))"), [1, 2, 3, 4]
    )
    self.assertEqual(
      execute("array(time([23,59,59,999999])+time([0,0,0,1]))"), [0, 0, 0, 0]
    )
    # age tests
    self.assertEqual(execute("age(now())"), [0, "seconds"])
    self.assertEqual(
      execute("age(dateTime([2000,1,1,1,1]),dateTime([2001,1,1,1,1]))"),
      [1, "year"]
    )
    self.assertEqual(
      execute("age(dateTime([2000,1,1,1,1]),dateTime([2000,2,1,1,1]))"),
      [1, "month"]
    )
    self.assertEqual(
      execute("age(dateTime([2000,1,1,1,1]),dateTime([2000,1,2,1,1]))"),
      [1, "day"]
    )
    self.assertEqual(
      execute("age(dateTime([2000,1,1,1,1]),dateTime([2000,1,1,2,1]))"),
      [1, "hour"]
    )
    self.assertEqual(
      execute("age(dateTime([2000,1,1,1,1]),dateTime([2000,1,1,1,2]))"),
      [1, "minute"]
    )
    self.assertEqual(
      execute("age(dateTime([2000,1,1,1,1,1]),dateTime([2000,1,1,1,1,2]))"),
      [1, "second"]
    )
    self.assertEqual(
      execute("""array(time([0,0]) - time([0,0,0,999999]))"""),
      [23, 59, 59, 1]
    )
    self.assertEqual(
      execute("""array(time([0,0]) + time([0,0,0,999999]))"""),
      [0, 0, 0, 999999]
    )

  def test_localize(self):
    pass
    #these tests are passing on computers with timezone set to UTC - not the case of TravisCI
    #test of non-DST time
    #if sys.version < "3":
    #self.assertEqual(execute("array(localize(dateTime([2000,1,1,10,10,1,0]),'Europe/Warsaw'))"), [2000,1,1,11,10,1,0])
    #test of DST time
    #self.assertEqual(execute("array(localize(dateTime([2000,7,1,10,10,1,0]),'Europe/Warsaw'))"), [2000,7,1,12,10,1,0])

  def test_builtin_type(self):
    self.assertEqual(execute("type([1,2,3,4]+[2,4])"), "array")
    self.assertEqual(execute("type({})"), "object")
    self.assertEqual(execute("type('')"), "str")

  def test_selector_with_empty_result(self):
    self.assertEqual(execute("$.missing is None"), True)
    self.assertEqual(execute("$.missing is not None"), False)

  def test_misc(self):
    self.assertEqual(execute(2), 2)
    self.assertEqual(execute('{"@aaa":1}.@aaa'), 1)
    self.assertEqual(execute('$ss.a'), None)
    self.assertEqual(execute("$..*[10]"), None)
    self.assertEqual(sorted(execute("keys({'a':1,'b':2})")), ['a', 'b'])
    self.assertRaises(ExecutionError, lambda: execute('keys([])'))
    self.assertRaises(ProgrammingError, lambda: execute('blah([])'))

  def test_optimizations(self):
    self.assertEqual(execute("$.*[@]"), execute("$.*"))
    self.assertIsInstance(execute_raw("$..*"), generator)
    self.assertIsInstance(execute_raw("$..* + $..*"), chain)
    self.assertIsInstance(execute_raw("$..* + 2"), chain)
    self.assertIsInstance(execute_raw("2 + $..*"), chain)
    self.assertEqual(execute("$.._id[0]"), 1)
    self.assertEqual(execute("sort($.._id + $.._id)[2]"), 2)
    self.assertIsInstance(execute("$.._id[2]"), int)
    self.assertEqual(
      execute2("$.store.book.(price)[0].price"),
      execute2("$.store.book[0].price")
    )

class ObjectPath_Paths(unittest.TestCase):
  def assertItemsEqual(self, a, b, m=None):
    try:
      return self.assertCountEqual(a, b, m)
    except: pass
    return unittest.TestCase.assertItemsEqual(self, a, b, m)

  def test_simple_paths(self):
    self.assertEqual(execute("$.*"), object1)
    self.assertEqual(execute("$.a.b.c"), None)
    self.assertEqual(execute("$.a.b.c[0]"), None)
    self.assertEqual(execute("$.__lang__"), "en")
    self.assertEqual(execute("$.test.o._id"), 2)
    self.assertEqual(execute("$.test.l._id"), [3, 4])
    self.assertEqual(execute("$.*[test].o._id"), 2)
    self.assertEqual(execute("$.*['test'].o._id"), 2)
    self.assertEqual(
      execute('[1,"aa",{"a":2,"c":3},{"c":3},{"a":1,"b":2}].(a,b)'), [{
        "a": 2
      }, {
        "a": 1,
        "b": 2
      }]
    )
    self.assertEqual(
      execute2("$.store.book.(price,title)[0]"), {
        "price": 8.95,
        "title": "Sayings of the Century"
      }
    )
    self.assertEqual(len(execute2("$..*['Lord' in @.title]")), 1)
    self.assertEqual(
      execute2("$..book.(price,title)"), [{
        'price': 8.95,
        'title': 'Sayings of the Century'
      }, {
        'price': 12.99,
        'title': 'Sword of Honour'
      }, {
        'price': 8.99,
        'title': 'Moby Dick'
      }, {
        'price': 22.99,
        'title': 'The Lord of the Rings'
      }]
    )
    self.assertEqual(
      execute2("sort($..(price,title),'price')"),
      [{
        'price': 8.95,
        'title': 'Sayings of the Century'
      }, {
        'price': 8.99,
        'title': 'Moby Dick'
      }, {
        'price': 12.99,
        'title': 'Sword of Honour'
      }, {
        'price': 19.95
      }, {
        'price': 22.99,
        'title': 'The Lord of the Rings'
      }]
    )
    self.assertIsInstance(execute("now().year"), int)

  def test_complex_paths(self):
    self.assertEqual(sorted(execute("$.._id")), [1, 2, 3, 4])
    self.assertEqual(execute("$..l"), object1["test"]["l"])
    self.assertEqual(execute("$..l.._id"), [3, 4])
    self.assertEqual(execute2("$.store.*"), object2["store"])
    self.assertEqual(
      execute2("$.store.book.author"),
      ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien']
    )
    #print()
    #print(execute2("$.store.book.(author,aaa)"))
    self.assertEqual(
      execute2("$.store.book.(author,aaa)"), [{
        "author": "Nigel Rees"
      }, {
        "author": "Evelyn Waugh"
      }, {
        "author": "Herman Melville"
      }, {
        "author": "J. R. R. Tolkien"
      }]
    )
    self.assertEqual(
      execute2("$.store.book.(author,price)"), [{
        'price': 8.95,
        'author': 'Nigel Rees'
      }, {
        'price': 12.99,
        'author': 'Evelyn Waugh'
      }, {
        'price': 8.99,
        'author': 'Herman Melville'
      }, {
        'price': 22.99,
        'author': 'J. R. R. Tolkien'
      }]
    )
    self.assertEqual(
      execute2("$.store.book.*[author]"),
      ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien']
    )
    self.assertEqual(
      execute2("$.store.book.*['author']"),
      ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien']
    )
    self.assertEqual(execute2("$.store.book"), object2["store"]["book"])
    self.assertEqual(
      list(execute2("$..author")),
      ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien']
    )

  def test_selectors(self):
    self.assertEqual(
      execute2("$.store.book[@.id is not null]"),
      [{
        'category': 'reference',
        'price': 8.95,
        'title': 'Sayings of the Century',
        'id': 1,
        'author': 'Nigel Rees'
      }]
    )
    self.assertEqual(len(execute2("$.store.book[@.id is null]")), 3)
    self.assertEqual(len(execute("$..*[@._id>2]")), 2)
    self.assertEqual(execute("$..*[3 in @.l._id]")[0], object1['test'])
    self.assertEqual(execute2("$.store..*[4 in @.k._id]")[0], object2['store'])
    self.assertEqual(execute("$..*[@._id>1 and @._id<3][0]"), {'_id': 2})
    # very bad syntax!!!
    self.assertEqual(
      sorted(execute2("$.store.book[@.price]")),
      sorted([8.95, 12.99, 8.99, 22.99])
    )
    self.assertEqual(
      execute3("$..*[@.x is 5.6 and @.y is 9.891].value"), ['bar']
    )

  def test_object_list(self):
    self.assertItemsEqual(execute3('values($.*).value'), ['foo', 'bar', 'foobar'])
    self.assertItemsEqual(execute3('keys($.*)'), ['item_1', 'item_2', 'item_3'])
    self.assertItemsEqual(
      execute4('map(values, $..root..response).value'), [5, 4, 0]
    )

#testcase2=unittest.FunctionTestCase(test_efficiency(2))
testcase1 = unittest.TestLoader().loadTestsFromTestCase(ObjectPath)
testcase2 = unittest.TestLoader().loadTestsFromTestCase(ObjectPath_Paths)

op_test = unittest.TestSuite([testcase1, testcase2])
#utils_interpreter=unittest.TestSuite([testcase2])
