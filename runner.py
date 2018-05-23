#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Original code: https://gist.github.com/mixstef/946fce67f49f147991719bfa4d0101fa
Sample grammar from p.242 of:
Grune, Dick, Jacobs, Ceriel J.H., "Parsing Techniques, A Practical Guide" 2nd ed.,Springer 2008.

FIRST sets
----------
See report

FOLLOW sets
-----------

See report
  

"""


import plex

class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass

class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	
	def create_scanner(self,text):
		""" Creates a plex scanner for a particular grammar """

		# define some pattern constructs
		letter = plex.Range("AZaz")
		boolean = plex.NoCase(plex.Str("true","false","t","f", "0", "1"))
		andoroperators = plex.Str("and", "or")
		notoperator = plex.Str("not")
		equal = plex.Str("=")

		v = plex.Rep1(letter)
		parenthesis = plex.Str("(",")")
		output = plex.Str("print")		
		spaces = plex.Any(" \t\n")

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(andoroperators,'AND/OR'),
			(notoperator,'NOT'),
			(boolean,'BOOLEAN'),
			(equal,'='),
			(parenthesis,plex.TEXT),
			(output,'PRINT'),
			(spaces,plex.IGNORE),
			(v, 'VARIABLE') #v for variable to match grammar rules given in report
			])
			
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,text)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()
	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,text):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for the input
		self.create_scanner(text)
		
		# call parsing logic
		self.stmt_list()

# The grammar rules

	def stmt_list(self):
		if self.la=='VARIABLE' or self.la=='PRINT':
			self.stmt()
			self.stmt_list()
		elif self.la is None:
			return
		else:
			raise ParseError("in stmt_list: VARIABLE or PRINT expected")

	def stmt(self):
		if self.la=='VARIABLE':
			self.match('VARIABLE')
			self.match('=')
			self.expr()
		elif self.la=='PRINT':
			self.match('PRINT')
			self.expr()
		else:
			raise ParseError("in stmt: VARIABLE or = or PRINT expected")


	def expr(self):
		if self.la=='(' or self.la=='VARIABLE' or self.la=='BOOLEAN' or self.la=='NOT':
			self.term()
			self.term_tail()
		else:
			raise ParseError("in expr: ( or VARIABLE or BOOLEAN expected ")

	def term_tail(self):
		if self.la=='AND/OR':
			self.andoroperators()
			self.term()
			self.term_tail()
		elif self.la==')' or self.la=='VARIABLE' or self.la=='PRINT':
			return
		elif self.la is None:
			return	
		else:
			raise ParseError("in term_tail: AND/OR expected")

	def term(self):
		if self.la=='(' or self.la=='VARIABLE' or self.la=='BOOLEAN':
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("in term: ( or VARIABLE or BOOLEAN expected")

	def factor_tail(self):
		if self.la=='AND/OR':
			self.andoroperators()
			self.factor()
			self.factor_tail()
		elif self.la==')' or self.la=='AND/OR' or self.la=='VARIABLE' or self.la=='PRINT':
			return
		elif self.la is None:
			return
		else:
			raise ParseError("in factor_tail: NOT expected")

	def factor(self):
		if self.la=='(' or self.la=='VARIABLE' or self.la=='BOOLEAN':
			self.notoperator()
			self.Fnotoperator()
		else:
			raise ParseError("in factor: ( or VARIABLE or BOOLEAN expected")

	def Fnotoperator(self):
		if self.la=='(':
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la=='VARIABLE':
			self.match('VARIABLE')
		elif  self.la=='BOOLEAN':
			self.boolean()
		else:
			raise ParseError("in Fnotoperator: ( or VARIABLE or BOOLEAN expected)")	

	def boolean(self):
		if self.la=='BOOLEAN':
			self.match('BOOLEAN')
		else:
			raise ParseError("in boolean: BOOLEAN expected")


	def andoroperators(self):
		if self.la=='AND/OR':
			self.match('AND/OR')
			# return('and/or')
		else:
			raise ParseError("in andoroperators: or expected")

	def notoperator(self):
			if self.la=='NOT':
				self.match('NOT')
				# return('not')
			elif self.la==')' or self.la=='VARIABLE' or self.la=='BOOLEAN': #From follow set
				return
			elif self.la is None:
				return
			else:
				raise ParseError("in notoperator : not expected")
			
		
# the main part of the programm

# create the parser object
parser = MyParser()

# enter input for parsing
#text = input('give some input>')
with open("input.txt","r") as text:

# parse text
	try:
		parser.parse(text)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))

