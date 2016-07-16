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

	def inc_time(self, seconds):
		"""Increment time by *seconds*"""
		self.time += int(seconds)

	def dec_time(self, seconds):
		"""Decrement time by *seconds*"""
		self.time -= int(seconds)

	def __int__(self):
		"""returns the total time for this category and subcategories"""
		sum = self.time
		if sum < 0:
			sum = 0
			self.time = 0
		for s in self.children:
			sum += int(s)
		return sum

	def time_str(self):
		"""Time string format in hours, minutes and seconds"""
		hours = int(self) / 3600
		mins = (int(self) % 3600) / 60
		secs = (int(self) % 60)
		my = ""
		if hours > 0:
			my += str(hours) + "h"
		if mins > 0:
			my += " " + str(mins) + "m"
		if secs >= 0:
			my += " " + str(secs) + "s"
		return my

	def __str__(self):
		"""return self as string"""
		if self.state == "play":
			first = " =>  "
		else:
			first = " "*5
		return "{0:5s}{1:1s} {2:<20s}{3:>12s}".format(first, self.shortcut, self.name, self.time_str())

class Tracker(object):
	"""Monitor for the categories and user interface"""
	version = "v0.7"

	def __init__(self):
		"""Init the monitor with a categories list containing the root category,
		and a reference to the categories currently being logged"""
		self.categories = {"":Category(None, "", "Total time")}
		self.running = []
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

			#just load keys of exactly one char
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
		"""Update the time for all the categories (they know if they are running or stopped)"""
		for cat in self.categories:
			self.categories[cat].update()

	def do(self, key):
		"""Play or pause the category specified by *key*"""
		curr = self.categories[key]
		curr.toogle()
		if curr.state == "play":
			self.running.append(curr)
		else:
			self.running.remove(curr)

	def pause_running(self):
		"""Stops all the clocks"""
		for cat in self.running:
			cat.pause()

	def continue_running(self):
		"""Continue running those previously stopped by pause_running"""
		for cat in self.running:
			cat.play()

	def str_recursive(self, initial, level):
		"""concat al the subcategory strings recursively"""
		l = []
		mycad = str(initial)
		l.append(mycad[:5] + "  "*level + mycad[5:])
		for c in initial.children:
			l.append(self.str_recursive(c, level+1))
		return "\n".join(l)

	def delete_category(self, cat):
		"""Removes the category with key *cat* and its subcategories"""
		for c in self.categories[cat].children:
			self.delete_category(c.shortcut)
		self.categories[cat].parent.children.remove(self.categories[cat])
		if self.categories[cat] in self.running:
			self.running.remove(self.categories[cat])
		del self.categories[cat]

	def __str__(self):
		"""return self as string, for debugging"""
		cad = ""
		for c in self.categories[""].children:
			cad += self.str_recursive(c, 0) + "\n"
		cad += "\n" + str(self.categories[""])
		return cad

class Pad(object):
	"""Class to manage all the writing to screen and reading from keyboard"""
	def __init__(self, screen):
		"""Initialise the curses pad and menu options"""
		self.screen = screen
		self.pad = curses.newpad(100,200)
		self.pad.nodelay(1)
		self.pad.keypad(True)
		self.pad.clear()
		self.make_menues()

	def make_menues(self):
		"""Fill al the posibilities in the two menues existent"""
		self.menu = []
		self.menu.append(["SPACE","Pause all the clocks"])
		self.menu.append(["CR","Make report"])
		self.menu.append(["DEL","Exit"])
		self.menu.append(["1","Select a category and move it"])
		self.menu.append(["2","Delete a category"])
		self.menu.append(["3","Insert a new category"])
		self.menu.append(["4","Increment time of a category"])
		self.menu.append(["5","Decrement time of a category"])
		self.move_menu = []
		self.move_menu.append(["1", "Finish moving"])
		self.move_menu.append(["UP", "Move up the category and all the subcategories"])
		self.move_menu.append(["DOWN", "Move down the category and all the subcategories"])
		self.move_menu.append(["LEFT", "Unindent the category and all the subcategories"])
		self.move_menu.append(["RIGHT", "Indent the category and all the subcategories"])

	def write_header(self):
		"""Write the header to the pad in the first two lines, useful after clearing it"""
		self.pad.addstr(1,5,"Track your time "+Tracker.version)
		self.pad.hline(2,1,"-",28)

	def write(self, line, col, string):
		"""write *string* to (*line*, *col*) pad position"""
		self.pad.addstr(line,col,str(string))

	def write_menu(self, line, menu):
		"""write *menu* starting in *line*"""
		for option in menu:
			self.pad.hline(line, 0, " ", 199)
			self.pad.addstr(line, 6-len(option[0]), option[0] + " " + option[1])
			line+=1

	def ymaxscr(self):
		"""return the maximum value possible for the lines"""
	  	return self.screen.getmaxyx()[0] - 1

	def xmaxscr(self):
		"""return the maximum value possible for the columns"""
	  	return self.screen.getmaxyx()[1] - 1

	def getkey(self):
		"""return the pressed key or -1 if nothing is in the input buffer"""
		return self.pad.getkey()

	def getstr(self):
		"""wait for a string to be inserted and <intro> pressed and returns that string"""
		self.pad.nodelay(0)
		str = self.pad.getstr()
		self.pad.nodelay(1)
		return str

	def say(self, msg):
		"""write *msg* to the last line available, for notifications"""
		self.clean_status_line()
		lastline = self.ymaxscr()
		self.write(lastline, 1, msg)
		self.refresh(lastline)

	def getyx(self):
		"""return current pad writing position"""
		return self.pad.getyx()

	def msg_and_wait_getkey(self, msg):
		"""notify *msg* and wait for a key to be pressed, return the pressed key"""
		self.pad.nodelay(0)
		self.say(msg)
		opt = self.pad.getkey()
		self.pad.nodelay(1)
		return opt

	def clean_status_line(self):
		"""Clean the notifications line"""
		self.pad.hline(self.ymaxscr(), 0, " ", 199)

	def clean(self):
		"""Clean the whole pad"""
		self.pad.clear()

	def refresh(self, line=None):
		"""Refresh the screen with the contents in pad, id *line* is specified only that line will be refreshed"""
		if line is not None:
			self.pad.refresh(line, 0, line, 0, line, self.xmaxscr())
		else:
			self.pad.refresh(0,0,0,0,self.ymaxscr(),self.xmaxscr())

def loop(stdscr, t):
	"""Main loop in the script, to use with curses.wrapper"""
	curses.noecho()
	curses.cbreak()

	pad = Pad(stdscr)

	exit = False
	while not exit:
	  try: #done to avoid kill by resizing, just cicle again with the new values of the window
		try:
			action = pad.getkey()
			if action == "KEY_BACKSPACE": #DEL action
				action = pad.msg_and_wait_getkey("Press DEL again to exit")
				if action == "KEY_BACKSPACE":
					exit = True
					continue
				action = -1
			if action == " ": #SPACE action
				t.pause_running()
				pad.msg_and_wait_getkey(" -- Clock paused.  Press any key to resume -- ")
				t.continue_running()
				action = -1
			if action == "1": #MOVE category action
				while action not in t.categories:
					action = pad.msg_and_wait_getkey("Select category to move")
				mvkey = action
				this = t.categories[mvkey]
				while action != "1":
					pad.clean()
					pad.write_header()
					pad.write(3,0,t)
					nexty = pad.getyx()[0] + 2
					pad.write_menu(nexty, pad.move_menu)
					pad.refresh()
					action = pad.msg_and_wait_getkey("Selected {}; Press 1 to finish; Press arrow keys to move".format(mvkey))
					if action == "KEY_UP":
						if this.parent.children[0] is not this:
							thisind = this.parent.children.index(this)
							this.parent.children.remove(this)
							this.parent.children.insert(thisind-1, this)
					elif action == "KEY_DOWN":
						if this.parent.children[-1] is not this:
							thisind = this.parent.children.index(this)
							this.parent.children.remove(this)
							this.parent.children.insert(thisind+1, this)
					elif action == "KEY_LEFT":
						if this.parent.shortcut != "":
							this.change_parent(this.parent.parent)
					elif action == "KEY_RIGHT":
						thisind = this.parent.children.index(this)
						if thisind > 0:
							this.change_parent(this.parent.children[thisind-1])
				action = -1
			if action == "2":
				while (action not in t.categories) and (action != "KEY_BACKSPACE"):
					action = pad.msg_and_wait_getkey("Select category to remove; DEL to cancel")
				delkey = action
				if action in t.categories:
					action = pad.msg_and_wait_getkey("Press 2 to remove; any other key to cancel")
					if action == "2":
						t.delete_category(delkey)
				action = -1
			if action == "3":
				while not action.isalpha():
					action = pad.msg_and_wait_getkey("Press key to use as shortcut for the new category, key repeat not allowed: ")
					if action in t.categories:
						action = "3"
				pad.say("Type string for the category. (it won't show until <enter> is pressed)")
				name = pad.getstr()
				t.categories[action] = Category(t.categories[""],action,name)
				action = -1
			if action == "4":
				while (action not in t.categories) and (action != "KEY_BACKSPACE"):
					action = pad.msg_and_wait_getkey("Select category to increment time; DEL to cancel")
				if action in t.categories:
					pad.say("How many seconds do you want to add: ")
					t.categories[action].inc_time(pad.getstr())
				action = -1
			if action == "5":
				while (action not in t.categories) and (action != "KEY_BACKSPACE"):
					action = pad.msg_and_wait_getkey("Select category to decrement time; DEL to cancel")
				if action in t.categories:
					pad.say("How many seconds do you want to remove: ")
					t.categories[action].dec_time(pad.getstr())
				action = -1

			pad.clean_status_line()
			t.do(action)
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			pass
		finally:
			pad.pad.nodelay(1)

		pad.clean()
		pad.write_header()
		t.update_all()
		pad.write(3,0,str(t))
		nexty = pad.getyx()[0] + 2 #Skip 2 lines from the end of the last written text
		pad.write_menu(nexty, pad.menu)
		pad.refresh()
		time.sleep(0.33)
	  except (KeyboardInterrupt, SystemExit):
	  	exit = True
	  except:
		pass
	return 0

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
