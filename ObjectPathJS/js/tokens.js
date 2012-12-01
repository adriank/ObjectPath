// tokens.js
// 2012-11-23

// (c) 2006 Douglas Crockford,
// Modified (c) 2012 by Adrian Kalbarczyk making it ObjectPath tokenizer.

// Produce an array of simple token objects from a string.
// A simple token object contains these members:
//      type: 'name', 'string', 'number', 'operator'
//      value: string or number value of the token
//      from: index of first character of the token
//      to: index of the last character + 1

if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {
        "use strict";
        if (this == null) {
            throw new TypeError();
        }
        var t = Object(this);
        var len = t.length >>> 0;
        if (len === 0) {
            return -1;
        }
        var n = 0;
        if (arguments.length > 1) {
            n = Number(arguments[1]);
            if (n != n) { // shortcut for verifying if it's NaN
                n = 0;
            } else if (n != 0 && n != Infinity && n != -Infinity) {
                n = (n > 0 || -1) * Math.floor(Math.abs(n));
            }
        }
        if (n >= len) {
            return -1;
        }
        var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);
        for (; k < len; k++) {
            if (k in t && t[k] === searchElement) {
                return k;
            }
        }
        return -1;
    }
}

String.prototype.tokens=function(D){
		var log=console.log
		D=D?D:false
    var c;                      // The current character.
    var from;                   // The index of the start of the token.
    var i = 0;                  // The index of the current character.
    var length = this.length;
    var n;                      // The number value.
    var q;                      // The quote character.
    var str;                    // The string value.
    var result = [];            // An array to hold the results.
		var expression=this

		var prefix = '<>.';
		var operators='+-*/%<>'+'[,]'+'{}:'+'()'
		var root='$'
		var current='@'
		var wildcard="*" //probalby will be treated as op
		var wordOperators=["and","or","not","in","not in","is","is not",""]
		var error=function(errString){
			try{
				console.error(errString+" at char "+this.from+":"+this.to+"<br/>"+expression.substring(0,this.position[0])+"<b>"+expression.substring(this.position[0],this.position[1])+"</b>"+expression.substring(this.position[1],expression.lenght))
			} catch(e){
				throw {
					"error":errString,
					"message":errString
				}
			}
		}

    var make = function (type, value, errorString) {
// Make a token object.
				if (errorString){
					error(errorString)
					return
				}
        return {
            type: type,
            value: value,
            position: [from,i]
					};
    };

// Begin tokenization. If the source string is empty, return nothing.

    if (!this) {
        return;
    }

// Loop through this text, one character at a time.

    c = this.charAt(i);
		//log("start "+this.charAt(i))
    while (c) {
        from = i;

// Ignore whitespace.

        if (c <= ' ') {
            i += 1;
            c = this.charAt(i);

// name.

        } else if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c=="_") {
            str = c;
            i += 1;
            for (;;) {
							c = this.charAt(i);
							if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
									(c >= '0' && c <= '9') || c === '_') {
								str += c;
								i += 1;
							} else {
								break;
							}
            }
						if (wordOperators.indexOf(str)>=0){
							var prevToken=result[result.length-1]
							if (str==="not" && prevToken && prevToken.value==="is"){
								var t=make('op','is not')
								t.position[0]=prevToken.position[0]
								result[result.length-1]=t
							}
							else if (str==="in" && prevToken && result[result.length-1].value==="not"){
								var t=make('op','not in')
								t.position[0]=prevToken.position[0]
								result[result.length-1]=t
							}
							else
								result.push(make('op', str));
						}
						else
	            result.push(make('name', str));

// number.

// A number cannot start with a decimal point. It must start with a digit,
// possibly '0'.

        } else if (c >= '0' && c <= '9') {
            str = c;
            i += 1;

// Look for more digits.

            for (;;) {
                c = this.charAt(i);
                if (c < '0' || c > '9') {
                    break;
                }
                i += 1;
                str += c;
            }

// Look for a decimal fraction part.

            if (c === '.') {
                i += 1;
                str += c;
                for (;;) {
                    c = this.charAt(i);
                    if (c < '0' || c > '9') {
                        break;
                    }
                    i += 1;
                    str += c;
                }
            }

// Look for an exponent part.

            if (c === 'e' || c === 'E') {
                i += 1;
                str += c;
                c = this.charAt(i);
                if (c === '-' || c === '+') {
                    i += 1;
                    str += c;
                    c = this.charAt(i);
                }
                if (c < '0' || c > '9') {
                    make('number', str, "Bad exponent");
                }
                do {
                    i += 1;
                    str += c;
                    c = this.charAt(i);
                } while (c >= '0' && c <= '9');
            }

// Make sure the next character is not a letter.

            if (c >= 'a' && c <= 'z') {
                str += c;
                i += 1;
                make('number', str, "Bad number");
            }

// Convert the string value to a number. If it is finite, then it is a good
// token.

            n = +str;
            if (isFinite(n)) {
                result.push(make('number', n));
            } else {
                make('number', str,"Bad number");
            }

// string

        } else if (c === '\'' || c === '"') {
            str = '';
            q = c;
            i += 1;
            for (;;) {
                c = this.charAt(i);
                if (c < ' ') {
                    make('str', str, c === '\n' || c === '\r' || c === '' ?
                        "Unterminated string." :
                        "Control character in string.", make('', str));
                }

// Look for the closing quote.

                if (c === q) {
                    break;
                }

// Look for escapement.

                if (c === '\\') {
                    i += 1;
                    if (i >= length) {
                        make('str', str, "Unterminated string");
                    }
                    c = this.charAt(i);
                    switch (c) {
                    case 'b':
                        c = '\b';
                        break;
                    case 'f':
                        c = '\f';
                        break;
                    case 'n':
                        c = '\n';
                        break;
                    case 'r':
                        c = '\r';
                        break;
                    case 't':
                        c = '\t';
                        break;
                    case 'u':
                        if (i >= length) {
                            make('str', str,"Unterminated string");
                        }
                        c = parseInt(this.substr(i + 1, 4), 16);
                        if (!isFinite(c) || c < 0) {
                            make('str', str,"Unterminated string");
                        }
                        c = String.fromCharCode(c);
                        i += 4;
                        break;
                    }
                }
                str += c;
                i += 1;
            }
            i += 1;
            result.push(make('str', str));
            c = this.charAt(i);

// combining - we have only >=, <=, ..

        } else if (prefix.indexOf(c) >= 0) {
            str = c;
            i += 1;
						c = this.charAt(i);
						if (str==="<" && c==="=")
							str="<="
						else if (str===">" && c==="=")
							str=">="
						else if (str==="." && c===".")
							str=".."
						if (str.length>1){
							i+=1
							c=this.charAt(i)
						}
            result.push(make('op', str));

// single-character operator

        } else {
            i += 1;
						if (c===root)
	            result.push(make('(root)', c));
						else if (c===current)
	            result.push(make('(current)', c));
						else if (operators.indexOf(c) >= 0)
	            result.push(make('op', c));
						else
							make('op', c, c+" is not an ObjectPath operator!")
            c = this.charAt(i);
        }
    }
		if (D) log("}tokens with",result)
    return result;
};
//D=true
//log("[1,2,4] + [3,5]".tokens())
