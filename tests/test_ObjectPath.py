#!/usr/bin/env python
# -*- coding: utf-8 -*-

from objectpath.core.interpreter import *
from random import randint, choice
import sys, unittest, os

sys.setrecursionlimit(20000)

object1={
	"__lang__":"en",
	"test":{
		"_id":1,
		"name":"aaa",
		"o":{
			"_id":2
		},
		"l":[
			{
				"_id":3,
				"aaa":"ddd",
				"false":2
			},
			{
				"_id":4
			}
		]
	}
}

object2={
	"store": {
		"book": [
			{ "category": "reference",
				"author": "Nigel Rees",
				"title": "Sayings of the Century",
				"price": 8.95
			},
			{ "category": "fiction",
				"author": "Evelyn Waugh",
				"title": "Sword of Honour",
				"price": 12.99
			},
			{ "category": "fiction",
				"author": "Herman Melville",
				"title": "Moby Dick",
				"isbn": "0-553-21311-3",
				"price": 8.99
			},
			{ "category": "fiction",
				"author": "J. R. R. Tolkien",
				"title": "The Lord of the Rings",
				"isbn": "0-395-19395-8",
				"price": 22.99
			}
		],
		"bicycle": {
			"color": "red",
			"price": 19.95
		},
		"k":[
			{
				"_id":4
			}
		]
	}
}

tree1=Tree(object1)
tree2=Tree(object2)

def execute(expr):
	return tree1.execute(expr)

def execute2(expr):
	return tree2.execute(expr)

class Utils_interpreter(unittest.TestCase):
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
		self.assertEqual(list(execute("[1,2,3]")), [1,2,3])
		self.assertEqual(list(execute("[false,null,true,'',\"\",2,2.0,{}]")), [False,None,True,'',"",2,2.0,{}])

	def test_objects(self):
		self.assertEqual(execute("{}"), {})
		self.assertEqual(execute("{a:1,b:false,c:'string'}"), {"a":1,"b":False,"c":'string'})
		self.assertEqual(execute("{'a':1,'b':false,'c':'string'}"), {"a":1,"b":False,"c":'string'})

	def test_arithm_add(self):
		self.assertEqual(execute("2+3"), 5)
		self.assertEqual(execute("2+3+4"), 9)
		self.assertEqual(execute("++3"), 3)

	def test_arithm_sub(self):
		self.assertEqual(execute("-1"), -1)
		self.assertEqual(execute("2-3"), 2-3)
		self.assertEqual(execute("2.2-3.4"), 2.2-3.4)
		self.assertEqual(execute("-+-3"), 3)
		self.assertEqual(execute("+-+3"), -3)

	def test_arithm_mul(self):
		self.assertEqual(execute("2*3*5*6"), 180)

	def test_arithm_mod(self):
		self.assertEqual(execute("2%3"), 2.0%3)
		self.assertEqual(execute("2.0%3"), 2.0%3)
		self.assertEqual(execute("float(2)%3"), float(2)%3)

	def test_arithm_div(self):
		self.assertEqual(execute("2/3"), 2.0/3)
		self.assertEqual(execute("2.0/3"), 2.0/3)
		self.assertEqual(execute("float(2)/3"), float(2)/3)

	def test_arithm_group(self):
		self.assertEqual(execute("2-3+4+5-7"), 2-3+4+5-7)
		self.assertEqual(execute("33*2/5-2"), 33*2/5.0-2)
		self.assertEqual(execute("33-4*5+2/6"), 33-4*5+2/6.0)
		#self.assertEqual(execute("2//3//4//5"), ('//', ('//', ('//', 2, 3), 4), 5))

	def test_arithm_parentheses(self):
		self.assertEqual(execute("2+2*2"), 6)
		self.assertEqual(execute("2+(2*2)"), 6)
		self.assertEqual(execute("(2+2)*2"), 8)
		self.assertEqual(execute("(33-4)*5+2/6"), (33-4)*5+2/6.0)
		self.assertEqual(execute("2/3/(4/5)*6"), 2/3.0/(4/5.0)*6)
		self.assertEqual(execute("((2+4))+6"), ((2+4))+6)

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
		self.assertEqual(execute("null or false or 0 or 0.0 or '' or [] or {}"), {})

	def test_logic_and(self):
		self.assertEqual(execute("1 and 2"), 2)
		self.assertEqual(execute("0 and 2"), 0)
		self.assertEqual(execute("'a' and false and 3"), False)
		self.assertEqual(execute("true and 1 and 1.0 and 'foo' and [1] and {a:1}"), {"a":1})

	def test_comparison_is(self):
		self.assertEqual(execute("2 is 2"), True)
		self.assertEqual(execute("'2' is 2"), True)
		self.assertEqual(execute("2 is '2'"), True)
		self.assertEqual(execute("2 is 2.0"), True)
		self.assertEqual(execute("0.1+0.2 is 0.3"), True)
		self.assertEqual(execute("[] is []"), True)
		self.assertEqual(execute("[1] is [1]"), True)

	def test_comparison_isnot(self):
		self.assertEqual(execute("3 is not 6"), True)
		self.assertEqual(execute("[] is not [1]"), True)

	def test_membership_in(self):
		self.assertEqual(execute("4 in [6,4,3]"),True)
		self.assertEqual(execute("4 in {4:true}"),True)
		self.assertEqual(execute("[2,3] in [6,4,3]"),True)

	def test_membership_notin(self):
		self.assertEqual(execute("4 not in []"), True)
		self.assertEqual(execute("1 not in {}"), True)
		self.assertEqual(execute("[2,5] not in [6,4,3]"),True)

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
		self.assertEqual(list(execute("[1,2,4] + [3,5]")), [1,2,4,3,5])
		self.assertEqual(execute('{"a":1,"b":2} + {"a":2,"c":3}'), {"a":2,"b":2,"c":3})

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
		self.assertEqual(execute("array('abc')"), ['a','b','c'])
		self.assertEqual(execute("array(dateTime([2011,4,8,12,0]))"), [2011,4,8,12,0,0,0])
		self.assertEqual(execute("array(date([2011,4,8]))"), [2011,4,8])
		self.assertEqual(execute("array(time([12,12,30]))"), [12,12,30,0])

	def test_builtin_arithmetic(self):
		self.assertEqual(execute("sum([1,2,3,4])"), sum([1,2,3,4]))
		self.assertEqual(execute("min([1,2,3,4])"), min([1,2,3,4]))
		self.assertEqual(execute("max([1,2,3,4])"), max([1,2,3,4]))
		self.assertEqual(execute("avg([1,2,3,4])"), 2.5)
		self.assertEqual(execute("avg([1,3,3,1])"), 2.0)
		self.assertEqual(execute("avg([1.1,1.3,1.3,1.1])"), 1.2000000000000002)
		self.assertEqual(execute("round(2/3)"), round(2.0/3))
		self.assertEqual(execute("round(2/3,3)"), round(2.0/3,3))

	def test_builtin_string(self):
		self.assertEqual(execute("replace('foobar','oba','baz')"), 'fobazr')
		self.assertEqual(execute("""escape('&lt;')"""), "&amp;lt;")
		self.assertEqual(execute("""escape('<"&>')"""), "&lt;&quot;&amp;&gt;")
		self.assertEqual(execute("""unescape('&lt;&quot;&amp;&gt;')"""), "<\"&>")
		self.assertEqual(execute("upper('aaa')"),"AAA")
		self.assertEqual(execute("lower('AAA')"),"aaa")
		self.assertEqual(execute("title('AAA aaa')"),"Aaa Aaa")
		self.assertEqual(execute("capitalize('AAA Aaa')"),"Aaa aaa")
		self.assertEqual(execute("split('aaa aaa')"),["aaa","aaa"])
		self.assertEqual(execute("split('aaaxaaa','x')"),["aaa","aaa"])
		self.assertEqual(execute("join(['aaą','aaę'],'ć')"),"aaąćaaę")
		self.assertEqual(execute("join(['aaa','aaa'])"),"aaaaaa")

	def test_builtin_arrays(self):
		self.assertEqual(execute("sort([1,2,3,4]+[2,4])"), [1,2,2,3,4,4])
		self.assertEqual(execute("reverse([1,2,3,4]+[2,4])"), [4,2,4,3,2,1])
		self.assertEqual(execute("len([1,2,3,4]+[2,4])"), 6)

	def test_builtin_time(self):
		import datetime
		self.assertIsInstance(execute("now()"),datetime.datetime)
		self.assertIsInstance(execute("age(now())"),tuple)
		self.assertIsInstance(execute("date()"), datetime.date)
		self.assertIsInstance(execute("date(now())"), datetime.date)
		self.assertIsInstance(execute("date([2001,12,30])"), datetime.date)
		self.assertIsInstance(execute("time()"), datetime.time)
		self.assertIsInstance(execute("time(now())"), datetime.time)
		self.assertIsInstance(execute("time([12,23])"), datetime.time)
		self.assertIsInstance(execute("time([12,23,21,777777])"), datetime.time)
		self.assertIsInstance(execute("dateTime(now())"), datetime.datetime)
		self.assertIsInstance(execute("dateTime([2001,12,30,12,23])"), datetime.datetime)
		self.assertIsInstance(execute("dateTime([2001,12,30,12,23,21,777777])"), datetime.datetime)
		self.assertIsInstance(execute("dateTime(date(),time())"), datetime.datetime)
		self.assertIsInstance(execute("dateTime(date(),[12,23])"), datetime.datetime)
		self.assertIsInstance(execute("dateTime(date(),[12,23,21,777777])"), datetime.datetime)
		self.assertIsInstance(execute("dateTime([2001,12,30],time())"), datetime.datetime)
		self.assertEqual(execute("array(time([12,30])-time([8,00]))"), [4,30,0,0])
		self.assertEqual(execute("array(time([12,12,12,12])-time([8,8,8,8]))"), [4,4,4,4])
		self.assertEqual(execute("array(time([12,12,12,12])-time([1,2,3,4]))"), [11,10,9,8])
		self.assertEqual(execute("array(time([12,00])-time([1,10]))"), [10,50,0,0])
		self.assertEqual(execute("array(time([1,00])-time([1,10]))"), [23,50,0,0])
		self.assertEqual(execute("array(time([0,00])-time([0,0,0,1]))"), [23,59,59,9999])
		self.assertEqual(execute("array(time([0,0])+time([1,1,1,1]))"), [1,1,1,1])
		self.assertEqual(execute("array(time([0,0])+time([1,2,3,4]))"), [1,2,3,4])
		self.assertEqual(execute("array(time([23,59,59,9999])+time([0,0,0,1]))"), [0,0,0,0])

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

class Utils_Paths(unittest.TestCase):
	def test_simple_paths(self):
		self.assertEqual(execute("$.*[0]"), object1)
		self.assertEqual(execute("$.a.b.c"), None)
		self.assertEqual(execute("$.a.b.c[0]"), None)
		self.assertEqual(execute("$.__lang__"), "en")
		self.assertEqual(execute("$.test.o._id"), 2)
		self.assertEqual(execute("$.test.l._id"), [3, 4])
		self.assertEqual(execute("$.*[test][0].o._id"), 2)
		self.assertEqual(execute("$.*['test'][0].o._id"), 2)
		self.assertIsInstance(execute("now().year"),int)

	def test_complex_paths(self):
		self.assertEqual(execute("$.._id"), [1, 2, 3, 4])
		self.assertEqual(execute("$..l"), object1["test"]["l"])
		self.assertEqual(execute("$..l.._id"), [3,4])
		self.assertEqual(execute2("$.store.*"), [object2["store"]])
		self.assertEqual(execute2("$.store.book.author"), ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'])
		self.assertEqual(execute2("$.store.book.*[author]"), ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'])
		self.assertEqual(execute2("$.store.book.*['author']"), ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'])
		self.assertEqual(execute2("$.store.book"), object2["store"]["book"])
		self.assertEqual(execute2("$..author"), ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'])

	def test_selectors(self):
		self.assertEqual(len(execute("$..*[@._id>2]")), 2)
		#self.assertEqual(execute("$..*[3 in @.l._id]")[0], object1.requestStorage['test'])
		#self.assertEqual(execute2("$.store..*[4 in @.k._id]")[0], object2.requestStorage['store'])
		#self.assertEqual(execute("$..*[@._id>1 and @._id<3][0]"), {'_id': 2})

#testcase2=unittest.FunctionTestCase(test_efficiency(2))
testcase1=unittest.TestLoader().loadTestsFromTestCase(Utils_interpreter)
testcase2=unittest.TestLoader().loadTestsFromTestCase(Utils_Paths)

utils_interpreter=unittest.TestSuite([testcase1,testcase2])
#utils_interpreter=unittest.TestSuite([testcase2])
