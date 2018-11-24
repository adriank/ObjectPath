#!/usr/bin/env python
# -*- coding: utf-8 -*-

def color(c, s):
  return '\033[%sm%s\033[0m' % (c, s)

def bold(s):
  return color(1, s)

def op(s):
  return color(32, bold(s))

def const(s):
  return color(36, bold(s))

def string(s):
  return color(33, bold(s))
