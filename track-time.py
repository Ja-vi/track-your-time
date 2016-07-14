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
			self.parent.children.append(self)

	def play(self):
		"""Continue logging time to this category"""
		self.start_time = int(time.time())
		self.state = "play"

	def pause(self):
		"""Pause logging time to this category"""
		self.state = "pause"

	def toogle(self):
		"""Quickly toogle between states"""
		if self.state == "pause":
			self.play()
		else:
			self.pause()

	def update(self):
		"""updates the time for this category"""
		if self.state == "play":
			delta = int(time.time())
			self.time += (delta - self.start_time)
			self.start_time = delta

	def change_parent(self, newparent):
		"""Make this category a subcategory of *newparent* if it is not the root category"""
		if self.parent is not None:
			self.parent.children.remove(self)
			newparent.children.append(self)
			self.parent = newparent

	def __int__(self):
		"""returns the total time for this category and subcategories"""
		sum = self.time
		for s in self.children:
			sum += int(s)
		return sum

	def time_str(self):
		hours = int(self) / 3600
		mins = (int(self) % 3600) / 60
		secs = (int(self) % 60)
		my = ""
		if hours > 0:
			my += str(hours) + "h"
		if mins > 0:
			my += " " + str(mins) + "m"
		if secs > 0:
			my += " " + str(secs) + "s"
		return my

	def __str__(self):
		"""return self as string"""
		return " "*5 + self.shortcut + " " + self.name + self.time_str()

class Tracker(object):
	"""Monitor for the categories and user interface"""

	def __init__(self):
		"""Init the monitor with a categories list containing the root category,
		and a reference to the categories currently being logged"""
		self.categories = {"":Category(None, "", "Total time")}
		self.config_file = None

	def load_config(self, filename):
		"""
		Loads the content of a config file in categories

		Structure of config file:
		p: project1
		- t: task1 in project1
		-- s: subtask of task1
		q: project2
		i: independent task

		"""
		self.config_file = filename
		with open(filename) as f:
			lines = f.readlines()

		config = {}
		for l in lines:
			s = [w.strip("-").strip() for w in l.split(":")]

			#just allow keys of exactly one char
			if len(s[0]) != 1:
				continue

			#and only unique keys
			if s[0] in config.keys():
				continue
			config[s[0]] = s[1]

			#TODO not subcategories loaded yet, all loaded as children of root category
			self.categories[s[0]] = Category(self.categories[""],s[0],s[1])

	def new_config(self, filename):
		"""Creates an empty file to write the config of the logger when closing"""
		self.config_file = filename
		with open(filename, "w") as f:
			pass

	def update_all(self):
		for cat in self.categories:
			self.categories[cat].update()

	def do(self, key):
		self.categories[key].toogle()

	def __str__(self):
		"""return self as string, for debugging"""
		return "\n".join([str(self.categories[key]) for key in self.categories])

def loop(stdscr, t):
	"""Main loop in the script, to use with curses.wrapper"""
	curses.noecho()
	curses.cbreak()
	stdscr.nodelay(1)
	stdscr.keypad(True)
	stdscr.clear()

	#print the header
	stdscr.addstr(1,5,"Track your time v0.5")
	stdscr.hline(2,1,"-",28)

	exit = False
	while not exit:
		try:
			action = stdscr.getkey()
			if action == "KEY_BACKSPACE":
				stdscr.nodelay(0)
				stdscr.addstr(10,1,"Press DEL again to exit")
				stdscr.refresh()
				action = stdscr.getkey()
				if action == "KEY_BACKSPACE":
					exit = True
					continue
				stdscr.nodelay(1)

			t.do(action)
		except:
			pass

		t.update_all()
		stdscr.addstr(3,1,str(t))
		stdscr.refresh()
		time.sleep(0.125)

def main():
	"""Script entry point"""
	t=Tracker()
	if len(sys.argv) > 1:
		t.load_config(sys.argv[1])
	else:
		try:
			t.load_config("default.rc")
		except IOError:
			t.new_config("default.rc")
		except:
			print("Error: unknown error")
			return -1
	curses.wrapper(loop, t)

if __name__ == '__main__':
    sys.exit(main())
