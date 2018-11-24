#!/usr/bin/env python
# -*- coding: utf-8 -*-

# move dbgMap outside
import inspect

class Debugger(object):
  dbg = None
  _debugStr = None
  dbgfn = None
  level = 40
  CUT_AFTER = 100
  CRITICAL = 50
  ERROR = 40
  WARNING = 30
  INFO = START = END = 20
  DEBUG = 10
  doDebug = False

  def __init__(self):
    self._debugStr = []
    self.dbgfn = self.consolelog
    self.dbgMap = {
        "debug": self.DEBUG,
        "info": self.INFO,
        "start": self.START,
        "end": self.END,
        "warning": self.WARNING,
        "error": self.ERROR,
        "critical": self.CRITICAL
    }
    try:
      self.doDebug = True
      self.level = self.dbgMap["debug"]
      self.info("All strings will be cut to %s chatacters." % self.CUT_AFTER)
    except (KeyError, TypeError):
      pass

  def debug(self, *s):
    if self.dbgfn and self.level <= self.DEBUG:
      self.dbgfn("DEBUG", s)

  def info(self, *s):
    if self.dbgfn and self.level <= self.INFO:
      self.dbgfn("INFO", s)

  def start(self, *s):
    if self.dbgfn and self.level <= self.INFO:
      self.dbgfn("START", s)

  def end(self, *s):
    if self.dbgfn and self.level <= self.INFO:
      self.dbgfn("END", s)

  def warning(self, *s):
    if self.dbgfn and self.level <= self.WARNING:
      self.dbgfn("WARNING", s)

  def error(self, *s):
    if self.dbgfn and self.level <= self.ERROR:
      self.dbgfn("ERROR", s)

  def critical(self, *s):
    if self.dbgfn and self.level <= self.CRITICAL:
      self.dbgfn("CRITICAL", s)

  def lineno(self):
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_back.f_back.f_lineno

  def consolelog(self, lvl, s):
    def f(x):
      try:
        if type(x) is unicode:
          x = x.encode("utf8")
      except NameError:
        pass
      if self.CUT_AFTER and type(x) is dict:
        s = []
        for i in x.items():
          s.append("'%s': %s" % (i[0], repr(i[1])[:self.CUT_AFTER]))
          if len(s[-1]) > self.CUT_AFTER:
            s.append("...")
        return "{\n\t" + ",\n\t".join(s) + "\n}"
      s = str(x).replace("\n", "").replace("\t", "")
      if self.CUT_AFTER and len(s) > self.CUT_AFTER:
        return s[:self.CUT_AFTER] + "..."
      else:
        return x

    if len(s) > 1:
      v = tuple(map(f, s[1:]))
      self._debugStr.append((lvl, s[0] % v))
      print(lvl + "@" + str(self.lineno()) + " " + s[0] % v)
    else:
      self._debugStr.append((lvl, s[0]))
      print(lvl + "@" + str(self.lineno()) + " " + f(s[0]))
