#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fan_theory_project.settings")

	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)

	# Load fixtures to prepoulate categories and tags
	if len(sys.argv) == 2 and sys.argv[1] == 'migrate':
		execute_from_command_line(['manage.py', 'loaddata', 'categories'])
		execute_from_command_line(['manage.py', 'loaddata', 'tags'])
