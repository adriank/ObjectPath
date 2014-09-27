#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2014 Adrian Kalbarczyk

# This program is free software: you can redistribute it and/or modify
# it under the terms of the version 3 of GNU General Public License as published by
# the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pymongo

class Mongo(object):
	#DB_NAME="default"
	DB_NAME="altix_pl"
	HOST="altix.asyncode.com"

	def __init__(self):
		self.conn=pymongo.Connection(host=self.HOST)[self.DB_NAME]

	def handle(self, fnName,args):
		if fnName=="mg_":
			pass

	def showColls(self):
		d={}
		for x in self.conn.collection_names():
			if x=="system.indexes":
				continue
			d[x]=self.conn[x].find()
		return d
	#def setDB(dbName):

mongo=Mongo()
