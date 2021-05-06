#!/usr/bin/python3

# Hardlinks / copies photos from the Syncthing directory to the by-date directory
# to ensure that a one-way sync can be maintained.

import datetime
import os
import pathlib
import sys
import shutil

import configparser
import string

import filecmp

conv = {
	'path': pathlib.Path,
	'template': string.Template,
}

config_file = configparser.ConfigParser(interpolation = None, converters = conv)

def section_path_priority(section: str):
	return config_file.getpath(section, 'source_dir')

def get_config_section(source_file: pathlib.Path):
	for section in sorted(config_file.sections(), key = section_path_priority, reverse = True):
		section_path = config_file.getpath(section, 'source_dir')
		if section_path not in source_file.resolve().parents:
			continue
		current_section = config_file[section]
		if 'glob' in current_section and not source_file.match(current_section.get('glob')):
			# validate glob-style pattern if specified
			continue
		return current_section
	return None

def main():
	source_file = pathlib.Path(sys.argv[1])
	
	if source_file.is_symlink() or not source_file.is_file():
		return
	
	config = get_config_section(source_file)
	if not config:
		raise ValueError(f"Could not determine section for file '{source_file}'")
	
	target_template = config.gettemplate('target_dir', fallback = None)
	if target_template is None:
		raise ValueError("Missing 'target_dir' config option")
	
	path_vars = {}
	
	mtime_format = config.get('mtime_format', fallback = None)
	if mtime_format:
		dt = datetime.datetime.fromtimestamp(os.path.getmtime(source_file))
		path_vars['mtime'] = dt.strftime(mtime_format)
	
	target_dir = pathlib.Path(target_template.safe_substitute(path_vars))
	target_file = target_dir / source_file.name
	
	target_file.parent.mkdir(exist_ok = True)
	
	if target_file.exists():
		if config.getboolean('reverse_symlink', fallback = False):
			if source_file.samefile(target_file) and not target_file.is_symlink():
				source_file.unlink()
				source_file.symlink_to(target_file)
				print(target_file, 'is link target for source')
			else:
				print(target_file, 'is not equal to source, not rsymlinking')
			return
		if source_file.samefile(target_file):
			# they're already linked together, do nothing
			print(target_file, 'points to the same file as source')
			return
		if filecmp.cmp(source_file, target_file, shallow = False):
			print(target_file, 'seems equal to source')
		if not config.getboolean('override_existing', fallback = False):
			print(target_file, 'exists, not overwriting')
			return
	elif config.getboolean('reverse_symlink', fallback = False):
		print(target_file, 'does not exist for rsymlinking')
		return
	
	if source_file.stat().st_dev == target_dir.stat().st_dev:
		# link within the same filesystem
		if target_file.exists() and config.getboolean('override_existing', fallback = False):
			os.unlink(target_file)
		os.link(source_file, target_file)
		print('link', source_file)
	elif config.getboolean('copy_ok', fallback = False):
		# copy file if allowed and on different filesystems
		shutil.copy2(source_file, target_file)
		print('copy', source_file)
	else:
		print(source_file, 'and', target_dir, 'are not on the same filesystem; not linking')

if __name__ == '__main__':
	xdg_conf = pathlib.Path(os.getenv('XDG_CONFIG_HOME') or (pathlib.Path.home() / '.config'))
	config_file.read(xdg_conf / 'st-archive' / 'config.ini')
	main()
