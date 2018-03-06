# -*- coding: utf-8 -*-

import sys
import re
from objectpath.core import *
from objectpath.utils.debugger import Debugger
from objectpath.core import ITER_TYPES, generator, chain
from objectpath.utils import flatten, filter_dict, timeutils, skip
import objectpath.utils.colorify as color
from objectpath.utils.json_ext import py2JSON

ObjectId = generateID = calendar = escape = escapeDict = unescape = unescapeDict = 0
EPSILON = 0.0000000000000001  # this is used in float comparison
OP_TOKENS = {
    "or": "o_or",
    "and": "o_and",
    "not": "o_not",
    "in": "o_in",
    "not in": "o_not_in",
    "is": "o_is_not_is",
    "is not": "o_is_not_is",

    "re": "o_re",
    "matches": "o_matches",

    "+": "o_plus",
    "-": "o_minus",
    "*": "o_star",
    "/": "o_slash",
    # "|": "o_vbar",
    # "&": "o_amper",
    "<": "o_less",
    ">": "o_greater",
    # "=": "o_equal",
    # ".": "o_dot",
    "%": "o_percent",
    # "{": "o_brace_left",
    # "}": "o_brace_right",
    # "==": "o_equal_equal",
    # "!=": "o_not_equal",
    "<=": "o_less_equal",
    ">=": "o_greater_equal",
    # "~": "o_tilde",
    # "^": "o_circumflex",
    # "<<": "o_left_shift",
    # ">>": "o_right_shift",
    # "**": "o_double_star",
    # "+=": "o_plus_equal",
    # "-=": "o_minus_equal",
    # "*=": "o_star_equal",
    # "/=": "o_slash_equal",
    # "%=": "o_percent_equal",
    # "&=": "o_amper_equal",
    # "|=": "o_vbar_equal",
    # "^=": "o_circumflex_equal",
    # "<<=": "o_left_shift_equal",
    # ">>=": "o_right_shift_equal",
    # "**=": "o_double_star_equal",
    # "//": "o_double_slash",
    # "//=": "o_double_slash_equal",
    # "@": "o_at",
    # "@=": "o_at_equal"
}

FN_TOKENS = {
    "sum": "fn_sum",
    "max": "fn_max",
    "min": "fn_min",
    "avg": "fn_avg",
    "round": "fn_round",

    # casting
    "int": "fn_int",
    "float": "fn_float",
    "str": "fn_str",
    "list": "fn_list",
    "array": "fn_list",

    # string
    "upper": "fn_upper",
    "lower": "fn_lower",
    "capitalize": "fn_capitalize",
    "title": "fn_title",
    "split": "fn_split",
    "slice": "fn_slice",
    "escape": "fn_escape",
    "unescape": "fn_unescape",
    "replace": "fn_replace",
    "sort": "fn_sort",
    "reverse": "fn_reverse",
    "map": "fn_map",
    "join": "fn_join",
    "count": "fn_count",
    "len": "fn_count",

    # time
    "now": "fn_now",
    "date": "fn_date",
    "time": "fn_time",
    "dateTime": "fn_dateTime",
    "age": "fn_age",
    "toMillis": "fn_toMillis",
    "localize": "fn_localize",

    # polygons
    "area": "fn_area",

    # misc
    "keys": "fn_keys",
    "type": "fn_type",
}


class Lexer(Debugger):
    def __init__(self, run, debug=False):
        if debug:
            super(Lexer, self).__init__()
        self._debug = debug
        self.run = run

    def o_error(self, *args):
        self.debug("%s not exists", args[0])

    def o_or(self, *args, **kwargs):
        if self._debug:
            self.debug("%s or %s", args[1], args[2])
        return self.run(args[1]) or self.run(args[2])

    def o_and(self, *args, **kwargs):
        if self._debug:
            self.debug("%s and %s", args[1], args[2])
        return self.run(args[1]) and self.run(args[2])

    def o_not(self, *args, **kwargs):
        fst = self.run(args[1])
        if self._debug:
            self.debug("doing not '%s'", fst)
        return not fst

    def o_in(self, *args, **kwargs):
        fst = self.run(args[1])
        snd = self.run(args[2])
        if self._debug:
            self.debug("doing '%s' in '%s'", args[1], args[2])
        if type(fst) in ITER_TYPES and type(snd) in ITER_TYPES:
            return any(x in max(fst, snd, key=len) for x in min(fst, snd, key=len))
        return self.run(args[1]) in self.run(args[2])

    def o_not_in(self, *args, **kwargs):
        fst = self.run(args[1])
        snd = self.run(args[2])
        if self._debug:
            self.debug("doing '%s' not in '%s'", args[1], args[2])
        if type(fst) in ITER_TYPES and type(snd) in ITER_TYPES:
            return not any(x in max(fst, snd, key=len) for x in min(fst, snd, key=len))
        return self.run(args[1]) not in self.run(args[2])

    def o_is_not_is(self, *args, **kwargs):
        op = args[0]
        if self._debug:
            self.debug("found operator '%s'", op)
        # try:
        fst = self.run(args[1])
        # except Exception as e:
        #     if D: self.debug("NOT ERROR! Can't execute args[1] '%s', error: '%s'. Falling back to orginal value.",args[1],str(e))
        #     fst=args[1]
        # try:
        snd = self.run(args[2])
        # except Exception as e:
        #     if D: self.debug("NOT ERROR! Can't execute args[2] '%s', error: '%s'. Falling back to orginal value.",args[2],str(e))
        #     snd=args[2]
        if op == "is" and fst == snd:
            return True
        # this doesn't work for 3 is not '3'
        # if op == "is not" and fst != snd:
        #     return True
        typefst = type(fst)
        typesnd = type(snd)
        if self._debug:
            self.debug("type fst: '%s', type snd: '%s'", typefst, typesnd)
        if typefst in STR_TYPES:
            if self._debug:
                self.info("doing string comparison '\"%s\" is \"%s\"'", fst, snd)
            result = fst == str(snd)
        elif typefst is float:
            if self._debug:
                self.info("doing float comparison '%s is %s'", fst, snd)
            result = abs(fst - float(snd)) < EPSILON
        elif typefst is int:
            if self._debug:
                self.info("doing integer comparison '%s is %s'", fst, snd)
            result = fst == int(snd)
        elif typefst is list and typesnd is list:
            if self._debug:
                self.info("doing array comparison '%s' is '%s'", fst, snd)
            result = fst == snd
        elif typefst is dict and typesnd is dict:
            if self._debug:
                self.info("doing object comparison '%s' is '%s'", fst, snd)
            result = fst == snd
        # else:
        #     try:
        #         global ObjectId
        #         if not ObjectId:
        #             from bson.objectid import ObjectId
        #         if typefst is ObjectId or typesnd is ObjectId:
        #             if D: self.info("doing MongoDB objectID comparison '%s' is '%s'",fst,snd)
        #             ret=str(fst)==str(snd)
        #         else:
        #             if D: self.info("doing standard comparison '%s' is '%s'",fst,snd)
        #             ret=fst is snd
        #     except Exception:
        #         pass
        if op == "is not":
            if self._debug:
                self.info("'is not' found. Returning %s", not result)
            return not result
        else:
            if self._debug:
                self.info("returning '%s' is '%s'='%s'", fst, snd, result)
            return result

    def o_plus(self, *args, **kwargs):
        if len(args) > 2:
            fst = self.run(args[1])
            snd = self.run(args[2])
            if None in (fst, snd):
                return fst or snd
            typefst = type(fst)
            typesnd = type(snd)
            if typefst is dict:
                try:
                    fst.update(snd)
                except Exception:
                    if type(snd) is not dict:
                        raise ProgrammingError("Can't add value of type %s to %s" % (
                            color.bold(PY_TYPES_MAP.get(type(snd).__name__, type(snd).__name__)),
                            color.bold("object")))
                return fst
            if typefst is list and typesnd is list:
                if self._debug:
                    self.debug("both sides are lists, returning '%s'", fst + snd)
                return fst + snd
            if typefst in ITER_TYPES or typesnd in ITER_TYPES:
                if typefst not in ITER_TYPES:
                    fst = [fst]
                elif typesnd not in ITER_TYPES:
                    snd = [snd]
                if self._debug:
                    self.debug("at least one side is generator and other is iterable, returning chain")
                return chain(fst, snd)
            if typefst in NUM_TYPES:
                try:
                    return fst + snd
                except Exception:
                    return fst + float(snd)
            if typefst in STR_TYPES or typesnd in STR_TYPES:
                if self._debug:
                    self.info("doing string comparison '%s' is '%s'", fst, snd)
                if sys.version_info[0] < 3:
                    if typefst is unicode:
                        fst = fst.encode("utf-8")
                    if typesnd is unicode:
                        snd = snd.encode("utf-8")
                return str(fst) + str(snd)
            try:
                timeType = timeutils.datetime.time
                if typefst is timeType and typesnd is timeType:
                    return timeutils.addTimes(fst, snd)
            except Exception:
                pass
            if self._debug:
                self.debug("standard addition, returning '%s'", fst + snd)
            return fst + snd
        else:
            return self.run(args[1])

    def o_minus(self, *args, **kwargs):
        if len(args) > 2:
            fst = self.run(args[1])
            snd = self.run(args[2])
            try:
                return fst - snd
            except Exception:
                typefst = type(fst)
                typesnd = type(snd)
                timeType = timeutils.datetime.time
                if typefst is timeType and typesnd is timeType:
                    return timeutils.subTimes(fst, snd)
        else:
            return - self.run(args[1])

    def o_star(self, *args, **kwargs):
        return self.run(args[1]) * self.run(args[2])

    def o_percent(self, *args, **kwargs):
        return self.run(args[1]) % self.run(args[2])

    def o_slash(self, *args, **kwargs):
        return self.run(args[1]) / float(self.run(args[2]))

    def o_greater(self, *args, **kwargs):
        if self._debug:
            self.debug("%s > %s, %s", args[1], args[2], args[1] > args[2])
        return self.run(args[1]) > self.run(args[2])

    def o_less(self, *args, **kwargs):
        return self.run(args[1]) < self.run(args[2])

    def o_greater_equal(self, *args, **kwargs):
        return self.run(args[1]) >= self.run(args[2])

    def o_less_equal(self, *args, **kwargs):
        return self.run(args[1]) <= self.run(args[2])

    def o_re(self, *args, **kwargs):
        return re.compile(self.run(args[1]))

    def o_matches(self, *args, **kwargs):
        return not not re.match(self.run(args[1]), self.run(args[2]))

    def __getitem__(self, item):
        return getattr(self, OP_TOKENS[item], self.o_error)


class Functions(Debugger):
    def __init__(self, run, debug=False):
        if debug:
            super(Functions, self).__init__()
        self._debug = debug
        self.run = run

    def o_error(self, *args):
        self.debug("Function %s not exists", args[0])

    def __getitem__(self, item):
        return getattr(self, FN_TOKENS[item], self.o_error)

    def fn_sum(self, *args, **kwargs):
        args = args[0]
        if type(args) in NUM_TYPES:
            return args
        return sum((x for x in args if type(x) in NUM_TYPES))

    def fn_max(self, *args, **kwargs):
        args = args[0]
        if type(args) in NUM_TYPES:
            return args
        return max((x for x in args if type(x) in NUM_TYPES))

    def fn_min(self, *args, **kwargs):
        args = args[0]
        if type(args) in NUM_TYPES:
            return args
        return min((x for x in args if type(x) in NUM_TYPES))

    def fn_avg(self, *args, **kwargs):
        args = args[0]
        if type(args) in NUM_TYPES:
            return args
        if type(args) not in ITER_TYPES:
            raise Exception("Argument for avg() is not an array")
        else:
            args = list(args)
        try:
            return sum(args) / float(len(args))
        except TypeError:
            args = [x for x in args if type(x) in NUM_TYPES]
            self.warning("Some items in array were ommited")
            return sum(args) / float(len(args))

    def fn_round(self, *args, **kwargs):
        return round(*args)

    # casting
    def fn_int(self, *args, **kwargs):
        return int(args[0])

    def fn_float(self, *args, **kwargs):
        return float(args[0])

    def fn_str(self, *args, **kwargs):
        return str(py2JSON(args[0]))

    def fn_list(self, *args, **kwargs):
        try:
            a = args[0]
        except IndexError:
            return []
        targs = type(a)
        if targs is timeutils.datetime.datetime:
            return timeutils.date2list(a) + timeutils.time2list(a)
        if targs is timeutils.datetime.date:
            return timeutils.date2list(a)
        if targs is timeutils.datetime.time:
            return timeutils.time2list(a)
        return list(a)

    # string
    def fn_upper(self, *args, **kwargs):
        return args[0].upper()

    def fn_lower(self, *args, **kwargs):
        return args[0].lower()

    def fn_capitalize(self, *args, **kwargs):
        return args[0].capitalize()

    def fn_title(self, *args, **kwargs):
        return args[0].title()

    def fn_split(self, *args, **kwargs):
        return args[0].split(*args[1:])

    def fn_slice(self, *args, **kwargs):
        if args and type(args[1]) not in ITER_TYPES:
            raise ExecutionError(
                "Wrong usage of slice(STRING, ARRAY). Second argument is not an array but %s." % color.bold(
                    type(args[1]).__name__))
        try:
            pos = list(args[1])
            if type(pos[0]) in ITER_TYPES:
                if self._debug:
                    self.debug("run slice() for a list of slicers")
                return (args[0][x[0]:x[1]] for x in pos)
            return args[0][pos[0]:pos[1]]
        except IndexError:
            if len(args) != 2:
                raise ProgrammingError(
                    "Wrong usage of slice(STRING, ARRAY). Provided %s argument, should be exactly 2." % len(
                        args))

    def fn_escape(self, *args, **kwargs):
        global escape, escapeDict
        if not escape:
            from objectpath.utils import escape, escapeDict
        return escape(args[0], escapeDict)

    def fn_unescape(self, *args, **kwargs):
        global unescape, unescapeDict
        if not unescape:
            from objectpath.utils import unescape, unescapeDict
        return unescape(args[0], unescapeDict)

    def fn_replace(self, *args, **kwargs):
        if sys.version_info[0] < 3 and type(args[0]) is unicode:
            args[0] = args[0].encode("utf8")
        return str.replace(args[0], args[1], args[2])

    def fn_sort(self, *args, **kwargs):
        if len(args) > 1:
            key = args[1]
            a = {"key": lambda x: x.get(key, 0)}
        else:
            a = {}
        args = args[0]
        if self._debug:
            self.debug("doing sort on '%s'", args)
        try:
            return sorted(args, **a)
        except TypeError:
            return args

    def fn_reverse(self, *args, **kwargs):
        args = args[0]
        try:
            args.reverse()
            return args
        except TypeError:
            return args

    def fn_map(self, *args, **kwargs):
        return map(lambda x: self.run(("fn", args[0], x)), args[1])

    def fn_count(self, *args, **kwargs):
        args = args[0]
        if args in (True, False, None):
            return args
        if type(args) in ITER_TYPES:
            return len(list(args))
        return len(args)

    def fn_join(self, *args, **kwargs):
        try:
            joiner = args[1]
        except Exception:
            joiner = ""
        try:
            return joiner.join(args[0])
        except TypeError:
            try:
                return joiner.join(map(str, args[0]))
            except Exception:
                return args[0]

    # time
    def fn_now(self, *args, **kwargs):
        return timeutils.now()

    def fn_date(self, *args, **kwargs):
        return timeutils.date(args)

    def fn_time(self, *args, **kwargs):
        return timeutils.time(args)

    def fn_dateTime(self, *args, **kwargs):
        return timeutils.dateTime(args)

    def fn_age(self, *args, **kwargs):
        # TODO move lang to localize() entirely!
        a = {}
        if len(args) > 1:
            a["reference"] = args[1]
        if len(args) > 2:
            a["lang"] = args[2]
        return list(timeutils.age(args[0], **a))

    def fn_toMillis(self, *args, **kwargs):
        args = args[0]
        if args.utcoffset() is not None:
            args = args - args.utcoffset()  # pylint: disable=E1103
        global calendar
        if not calendar:
            import calendar
        return int(calendar.timegm(args.timetuple()) * 1000 + args.microsecond / 1000)

    def fn_localize(self, *args, **kwargs):
        if type(args[0]) is timeutils.datetime.datetime:
            return timeutils.UTC2local(*args)

    # polygons
    def fn_area(self, *args, **kwargs):
        def segments(p):
            p = list(map(lambda x: x[0:2], p))
            return zip(p, p[1:] + [p[0]])

        return 0.5 * abs(sum(x0 * y1 - x1 * y0
                             for ((x0, y0), (x1, y1)) in segments(args[0])))

    # misc
    def fn_keys(self, *args, **kwargs):
        try:
            return list(args[0].keys())
        except AttributeError:
            raise ExecutionError(
                "Argument is not " + color.bold("object") + " but %s in keys()" % color.bold(
                    type(args[0]).__name__))

    def fn_type(self, *args, **kwargs):
        ret = type(args[0])
        if ret in ITER_TYPES:
            return "array"
        if ret is dict:
            return "object"
        return ret.__name__
