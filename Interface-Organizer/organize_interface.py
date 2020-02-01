#!/usr/bin/python
import argparse
import os
from os import path
import collections
from collections import defaultdict

import menu_mapping

def main():
	parser = argparse.ArgumentParser()
	#
	parser.add_argument('interface_file', help='path to interface.txt (usually in DF/data/init/)')
	#
	args=parser.parse_args()
	run(args)
def run(args):
	interface_file = args.interface_file
	print('Organizing keybindings in %s...' % path.abspath(interface_file))
	parse_interface(interface_file)
	print('...Done!')
	pass
def parse_interface(filepath):
	token_list = []
	with open(filepath, 'rb') as fin:
		token = read_next(fin)
		while token != None:
			#print('[%s]'%token)
			token_list.append(token)
			token = read_next(fin)
	
	menu_map = defaultdict(lambda: {})
	bind_token = b''
	menu_name = b''
	for n in range(0,len(token_list)):
		token = token_list[n]
		if token.startswith(b'BIND:'):
			# start of key bindings
			bind_token = token
			menu_name = get_menu_for(bind_token)
			if bind_token not in menu_map[menu_name]:
				menu_map[menu_name][bind_token] = []
		else:
			menu_map[menu_name][bind_token].append(token)
	#
	menus = set(menu_mapping.LUT.values())
	
	for menu_name in menus:
		#key_tokens = []
		#for bind_token in menu_map[menu_name]:
		#	key_tokens += binding_map[bind_token]
		#conflicts = check_for_conflicts(key_tokens)
		menu_binding_map = menu_map[menu_name]
		conflicts = check_for_conflicts(menu_binding_map)
		if len(conflicts) > 0:
			print('%s conflicts in menu %s:' % (
				len(conflicts), 
				menu_name ) )
			for c in conflicts:
				print('\t[%s][%s] conflicts with [%s][%s]'%c)
			
def get_menu_for(bind_token):
	token_type, token_name, token_repeat = bind_token.split(b':')
	if token_name in menu_mapping.LUT:
		return menu_mapping.LUT[token_name]
	else:
		raise Exception("%s not in menu_mappings.LUT!" % token_name)
def menu_analysis(binding_list):
	# return a list of all prefixes that appear more than 2 times
	pass

def check_for_conflicts(binding_key_map):
	conflicts = []
	tested_list = []
	for b1 in binding_key_map:
		tested_list.append(b1)
		for k1 in binding_key_map[b1]:
			for b2 in binding_key_map:
				if b2 in tested_list:
					continue
				for k2 in binding_key_map[b2]:
					if are_equivalent(k1, k2):
						conflicts.append( (b1, k1, b2, k2) )
	return set(conflicts)
_UPPER=[b'~', b'!', b'@', b'#', b'$', b'%', b'^', b'&', b'*', b'(', b')', b'_', b'+', b'Q', b'W', b'E', b'R', b'T', b'Y', b'U', b'I', b'O', b'P', b'{', b'}', b'|', b'A', b'S', b'D', b'F', b'G', b'H', b'J', b'K', b'L', b':', b'"', b'Z', b'X', b'C', b'V', b'B', b'N', b'M', b'<', b'>', b'?']
_LOWER=[b'`', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'0', b'-', b'=', b'q', b'w', b'e', b'r', b't', b'y', b'u', b'i', b'o', b'p', b'[', b']', b'\\', b'a', b's', b'd', b'f', b'g', b'h', b'j', b'k', b'l', b';', b'\'', b'z', b'x', b'c', b'v', b'b', b'n', b'm', b',', b'.', b'/']
def are_equivalent(token1, token2):
	if to_sym_token(token1) == to_sym_token(token2):
		return True
	return False
def to_sym_token(token):
	if token.startswith(b'KEY:'):
		if token[4] in _LOWER:
			return b'SYM:0:'+token[4]
		if token[4] in _UPPER:
			return b'SYM:1:'+_LOWER[_UPPER.index(token[4])]
	return token
def read_next(readable):
	token = b''
	c = readable.read(1)
	while c != b'[' and len(c) > 0:
		c = readable.read(1)
	if c == '':
		# end of file
		return None
	while c != b']' and len(c) > 0:
		c = readable.read(1)
		token += c
	
	if len(token) == 0:
		return None
	if token.endswith( b':]') and not token.endswith( b'::]'):# special cases: [KEY:]], [SYM:#:]], [KEY::], [SYM:#::]
		return token
	return token[:-1]

if __name__ == '__main__':
	main()
