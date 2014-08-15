var object={
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

var op=new objectPath(object)
var assertEqual=function(l,r,jsonCmp){
	//op.setDebug(true)
	var ret
	try{
		if (jsonCmp)
			ret=JSON.stringify(op.execute(l))===JSON.stringify(r)
		else
			ret=op.execute(l)===r
	} catch(e){
		console.log(e)
	}
	if (!ret){
		op.setDebug(true)
		op.execute(l)
		op.setDebug(false)
		throw {
			"error":l+" is "+JSON.stringify(r)+" not working"
		}
	}
	console.log("testing "+l+" is "+JSON.stringify(r)," -> OK")
}

//simpleType tests
assertEqual("null", null)
assertEqual("true", true)
assertEqual("false", false)
assertEqual("''", "")
assertEqual('""', "")
assertEqual("2+2", 4)
assertEqual("2.0", 2.0)
//array tests
assertEqual("[]", [],"JSON")
//assertEqual("[{}]", [{}],"JSON")
assertEqual("[1,2,3]", [1,2,3],"JSON")
//assertEqual("[false,null,true,'',\"\",2,2.0,{}]", [false,null,true,'',"",2,2.0,{}],"JSON")
//object tests
//assertEqual("{}", {},"JSON")
//assertEqual("{a:1,b:false,c:'string'}", {"a":1,"b":false,"c":'string'})
//assertEqual("{'a':1,'b':false,'c':'string'}", {"a":1,"b":false,"c":'string'})
//arithm:add tests
assertEqual("2+3", 5)
assertEqual("2+3+4", 9)
//assertEqual("++3", 3)
//arithm:sub tests
assertEqual("-1", -1)
assertEqual("2-3", 2-3)
assertEqual("2.2-3.4", 2.2-3.4)
//assertEqual("-+-3", 3)
//assertEqual("+-+3", -3)
//arithm:mul tests
assertEqual("2*3*5*6", 180)
//arithm:mod tests
assertEqual("2%3", 2.0%3)
assertEqual("2.0%3", 2.0%3)
//assertEqual("float(2)%3", float(2)%3)
//arithm:div tests
assertEqual("2/3", 2.0/3)
assertEqual("2.0/3", 2.0/3)
//assertEqual("float(2)/3", 2.0/3)
//arithm:group tests
assertEqual("2-3+4+5-7", 2-3+4+5-7)
assertEqual("33*2/5-2", 33*2/5.0-2)
assertEqual("33-4*5+2/6", 33-4*5+2/6.0)
assertEqual("2+2*2", 6)
//arithm:parentheses tests
assertEqual("2+(2*2)", 6)
assertEqual("(2+2)*2", 8)
assertEqual("(33-4)*5+2/6", (33-4)*5+2/6.0)
assertEqual("2/3/(4/5)*6", 2/3.0/(4/5.0)*6)
assertEqual("((2+4))+6", ((2+4))+6)
//logic:negatives
assertEqual("not false", true)
assertEqual("not null", true)
assertEqual("not 0", true)
assertEqual("not 0.0", true)
assertEqual("not ''", true)
assertEqual("not []", false)
//assertEqual("not {}", true)
//logic:not
assertEqual("not false", true)
assertEqual("not not not false", true)
assertEqual("1 or 2", 1)
assertEqual("0 or 2", 2)
assertEqual("'a' or 0 or 3", 'a')
//assertEqual("null or false or 0 or 0.0 or '' or [] or {}", {})
assertEqual("null or false or 0 or 0.0 or ''", '')

//def test_logic_and(:
assertEqual("1 and 2", 2)
assertEqual("0 and 2", 0)
assertEqual("'a' and false and 3", false)
//assertEqual("true and 1 and 1.0 and 'foo' and [1] and {a:1}", {"a":1},"JSON")

//def test_comparison_is(:
assertEqual("2 is 2", true)
assertEqual("'2' is 2", true)
assertEqual("2 is '2'", true)
assertEqual("2 is 2.0", true)
assertEqual("[] is []", true)
assertEqual("[1] is [1]", true)

//def test_comparison_isnot(:
assertEqual("3 is not 6", true)
assertEqual("[] is not [1]", true)
//def test_membership_in(self):
assertEqual("4 in [6,4,3]",true)
//assertEqual("4 in {4:true}",true)

////def test_membership_notin(self):
assertEqual("4 not in []", true)
//assertEqual("1 not in {}", true)

////def test_complex(self):
assertEqual("23 is not 56 or 25 is 57", true)
assertEqual("2+3/4-6*7>0 or 10 is not 11 and 14", 14)
//def test_comparison_lt(self):
assertEqual("2<3", true)
assertEqual("3<3", false)
assertEqual("2<=2", true)
assertEqual("2<=1", false)

//def test_comparison_gt(self):
assertEqual("5>4", true)
assertEqual("5>5", false)
assertEqual("5>=5", true)

//def test_concatenation(self):
assertEqual("'a'+'b'+\"c\"", 'abc')
assertEqual("'5'+5", '55')
assertEqual("5+'5'", 10)
assertEqual("[1,2,4] + [3,5]", [1,2,4,3,5],"JSON")
//assertEqual('{"a":1,"b":2} + {"a":2,"c":3}', {"a":2,"b":2,"c":3})
//def test_builtin_casting(self):
//assertEqual("str('foo')", 'foo')
//assertEqual("str(1)", '1')
//assertEqual("str(1.0)", '1.0')
//assertEqual("str(1 is 1)"), 'true')
//assertEqual("int(1)", 1)
//assertEqual("int(1.0)", 1)
//assertEqual("int('1')", 1)
//#Python can't handle that
//#assertEqual("int('1.0')", 1)
//assertEqual("float(1.0)", 1.0)
//assertEqual("float(1)", 1.0)
//assertEqual("float('1')", 1.0)
//assertEqual("float('1.0')", 1.0)
//assertEqual("array()", [])
//assertEqual("array([])", [])
//assertEqual("array('abc')", ['a','b','c'])
//assertEqual("array(dateTime([2011,4,8,12,0]))", [2011,4,8,12,0,0,0])
//assertEqual("array(date([2011,4,8]))", [2011,4,8])
//assertEqual("array(time([12,12,30]))", [12,12,30,0])
//def test_simple_paths(self):
assertEqual("$", object)
assertEqual("$.*[0]", object,"JSON")
assertEqual("$.a.b.c", null)
assertEqual("$.a.b.c[0]", null)
assertEqual("$.__lang__", "en")
assertEqual("$.test.o._id", 2)
assertEqual("$.test.l._id", [3, 4],"JSON")
assertEqual("$.*[test][0].o._id", 2)
assertEqual("$.*['test'][0].o._id", 2)
//assertIsInstance("now().year",int)
//def test_complex_paths(self):
assertEqual("$.._id", [1, 2, 3, 4],"JSON")
assertEqual("$..l[0]", object["test"]["l"])
assertEqual("$..l.._id", [3,4],"JSON")
op.setData(object2)
//self.assertEqual(execute2("$.store.*"), env2.requestStorage["store"])
assertEqual("$.store.book.author", ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'],"JSON")
assertEqual("$.store.book.*[author]", ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'],"JSON")
assertEqual("$.store.book.*['author']", ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'],"JSON")
assertEqual("$.store.book", object2["store"]["book"],"JSON")
assertEqual("$..author", ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien'],"JSON")

//def test_selectors(self):
//assertEqual("$.store..*[4 in @.k._id]", object2['store'])
op.setData(object)
//assertEqual("$..*[@._id>2]", 2)
//assertEqual("$..*[3 in @.l._id]", env1.requestStorage['test'])
//assertEqual("$..*[@._id>1 and @._id<3][0]", {'_id': 2},"JSON")
