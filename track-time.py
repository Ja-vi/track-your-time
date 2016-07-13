#!/usr/bin/env python
# coding: utf-8

"""Script to log time while you work on projects.
Keep track of how you are using your time,
and make reports about that"""

import time
import sys
import curses

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
		self.children = []
		self.state = "pause"
		if parent is not None:
			"""add self to parent.children"""

	def play(self):
		"""Continue logging time to this category"""
		self.start_time = time.time()
		self.state = "play"
		pass

	def pause(self):
		"""Pause logging time to this category"""
		self.state = "pause"
		pass

	def update(self):
		"""updates the time for this category"""
		if self.state is "play":
			self.time += (time.time() - self.start_time())

	def change_parent(self, newparent):
		"""Make this category a subcategory of *newparent*"""
		pass

	def __int__(self):
		"""returns the total time for this category and subcategories"""
		sum = self.time
		for s in self.children:
			sum += int(s)
		return sum

	def __str__(self):
		"""return self as string, for debugging"""
		return "<" + "-".join([self.shortcut, self.name, str(int(self))]) + ">"

class Tracker(object):
	"""Monitor for the categories and user interface"""

	def __init__(self):
		"""Init the monitor with a categories list containing the root category,
		and a reference to the categories currently being logged"""
		self.categories = [Category(None, "T", "Total time")]
		self.running = []
		self.config_file = None

	def load_config(self, filename):
		"""
		Loads the content of a config file in categories
		case insensitive

		Structure of config file:
		p: project1
		- t: task1 in project1
		-- s: subtask of task1
		q: project2
		i: independent task

		just single caracter allowed as shortcut
		"""
		self.config_file = filename

	def new_config(self, filename):
		"""Creates an empty file to write the config of the logger when closing"""
		self.config_file = filename
		with open(filename, "w") as f:
			pass

	def __str__(self):
		"""return self as string, for debugging"""
		return "[" + ", ".join([str(el) for el in self.categories]) + "]"

def loop(clrscr):
	"""Main loop in the script, to use with ncurses wrapper"""
	pass

def main():
	"""Script entry point"""
	t=Tracker()
	if len(sys.argv) > 1:
		t.load_config(sys.argv[1])
	else:
		try:
			t.load_config("prueba.rc")
		except:
			t.new_config("default.rc")
	print(t)
	curses.wrapper(loop)

if __name__ == '__main__':
    sys.exit(main())
