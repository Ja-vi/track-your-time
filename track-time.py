#!/usr/bin/env python
# coding: utf-8

"""Script to log time while you work on projects.
Keep track of how you are using your time,
and make reports about that"""

import time

class Category(object):
	"""Each of the projects and tasks, they can be nested"""
	def __init__(self, parent, shortcut, name, time=0):
		"""Basic initialization,
		*parent* for nested tasks,
		*shortcut* is the key to press to start logging,
		*name* the name or short definition of the task,
		provide a *time* to start it with a diferent seconds count, useful for persistence"""
		self.shortcut = shortcut
		self.name = name
		self.time = time
		self.parent = parent

class Tracker(object):
	"""Monitor for the categories and user interface"""
	def __init__(self):
		"""Init the monitor with an empty categories list"""
		self.categories = []

	def load_config(self, filename):
		"""
		Loads the content of the initial config file in memory
		"""
		f = open(filename)
		self.config = {}
		for line in f.readlines():
			splitted = line.split(":")
			try:
				print(splitted[0].strip())
				self.config[splitted[0].strip()]
				print("Error: repeted key in config file.")
				return
			except:
				pass
			self.config[splitted[0].strip()] = splitted[1].strip()

t=Tracker()
t.load_config("prueba.rc")
print(t.config)
