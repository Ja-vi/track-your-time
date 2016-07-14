track-your-time
===============

Motivation
----------

I created this program because I was using worklog to track the time I used
in projects, and I wanted to make some changes to the program and increase
functionality.

Extra functionality
-------------------

I also would like to create an easier interface and cleaner persistence system.

Configuration File
------------------

The configuration file is formed of lines where each line represent one Category.

A category is specified with _shortcut_ : _name-or-short-definition_

The following is an example of config file:

> c: cooking
> 
> d: developing
> 
> t: do the thing

2 things to remark here:
+ shortcuts should be one single character
+ shortcuts are case sensitive, c and C represent different elements

Execution
---------

To execute it, run:

	python track-time.py

If no argument is used it with try to load the default.rc config file, 
and if that does not exist, it will create it empty to add projects and 
tasks from the interface.

You can also run:
	
	python track-time.py configuration.rc

to have it load configuration.rc options.

License
-------

This project is licensed under GPLv3.0 please see attached license if in doubt
of restrictions.
