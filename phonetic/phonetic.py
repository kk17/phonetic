#!/usr/bin/env python
# -*- coding:utf-8 -*-

from os import path

_here = path.abspath(path.dirname(__file__))

class Pronunciation(object):
	"""docstring for Pronunciation"""
	def __init__(self, character, pronunciation, use_cases=None, explanation=None):
		super(Pronunciation, self).__init__()
		self.character = character
		self.pronunciation = pronunciation
		self.use_cases = use_cases
		self.explanation = explanation
		#异读字
		self.variant = False
		#粤语用词
		self.cantonese = False
		#人名，地名
		self.specific = False
		#通假字
		self.interchangeable = False

	def pretty(self):
		ret = "%s\t%s" % (self.character,self.pronunciation)
		if self.explanation:
			ret += "\n"
			ret += self.explanation
		if self.use_cases:
			ret += "\n"
			ret += u"，".join(self.use_cases)
		return ret

	def __str__(self):
		ret = self.pretty()
		ret += "\nvariant:" + str(self.variant)
		ret += "\ncantonese:" + str(self.cantonese)
		ret += "\nspecific:" + str(self.specific)
		ret += "\ninterchangeable:" + str(self.interchangeable)
		return ret.encode("utf-8")

import re

#异读字
_p_variant = re.compile(u"异读字|異讀字")
#粤语用词
_p_cantonese = re.compile(u"粤语用字|粵語用字")
#人名，地名
_p_specific = re.compile(u"人名|地名|姓氏|复姓|複姓|县名|縣名|国名|國名")
#通假字
_p_interchangeable = re.compile(u"同「.」字|通「.」字")

_p_other = re.compile(u"助词|助詞")

# m = _p_interchangeable.search(u"同「與」fd通「拯」字")
# if m:
# 	g = m.group()
# 	print type(g)
# 	print repr(g)
# 	ge = g.encode("utf-8")
# 	print repr(ge)
# 	print ge
# else:
# 	print "not found"
		

def _parse_line(line):
	line = line.strip()
	sp = line.split("\t")
	if len(sp) == 3:
		character = sp[0]
		# print character.encode("utf-8")
		pronunciation = sp[1]
		# print pronunciation.encode("utf-8")
		p = Pronunciation(character,pronunciation)
		use_cases = None
		explanation = None
		ue = sp[2]
		if ue:
			flag = False
			if _p_variant.search(ue):
				p.variant = True
				flag = True
			if _p_interchangeable.search(ue):
				p.interchangeable = True
				flag = True
			if _p_cantonese.search(ue):
				p.cantonese = True
				flag = True
			if _p_specific.search(ue):
				p.specific = True
				flag = True
			if _p_other.search(ue):
				flag = True
			# print sp[2].encode("utf-8")
			sp2 = ue.split(u"；")
			if len(sp2) > 1 and not sp2[0].startswith("("):
				use_cases = sp2[0].split(u"，")
				explanation = u"；".join(sp2[1:])
			else:
				# if sp2[0].startswith("("):
				if flag:
					explanation = ue
				else:
					use_cases = ue.split(u"，")
		p.use_cases = use_cases
		p.explanation = explanation
		return p

	return None		


def mix_notations(in_str,rlist):
	result = ""
	for c,p in zip(in_str,rlist):
		result+= c
		if p:
			result += "("+p+")"
	return result

class NotationResult(object):
	"""docstring for NotationResult"""
	def __init__(self, in_str,plist):
		super(NotationResult, self).__init__()
		self.in_str = in_str
		self.plist = plist

	def pretty(self):
		return mix_notations(self.in_str, self.plist)

	def __str__(self):
		return self.pretty().encode("utf-8")

class PronunciationsResult(object):
	"""docstring for PronunciationsResult"""
	def __init__(self, character,plist):
		super(PronunciationsResult, self).__init__()
		self.character = character
		self.plist = plist

	def pretty(self):
		prettys = [p.pretty() for p in self.plist]
		return "\n---------\n".join(prettys)

	def __str__(self):
		return self.pretty().encode("utf-8")
		
class CharactersResult(object):
	"""docstring for CharactersResult"""
	def __init__(self,pronunciation, plist):
		super(CharactersResult, self).__init__()
		self.pronunciation = pronunciation
		self.plist = plist

	def pretty(self):
		prettys = [p.character for p in self.plist]
		return ",".join(prettys)

	def __str__(self):
		return self.pretty().encode("utf-8")
		
		
		

import codecs
class NotationAdder(object):
	"""docstring for NotationAdder"""
	def __init__(self, datafile):
		super(NotationAdder, self).__init__()
		self.datafile = datafile
		char_map = {}
		pronon_map = {}
		lines = codecs.open(datafile,"r","utf-8").readlines()
		for line in lines:
			# print line
			p = _parse_line(line)
			if p:
				# print p
				# print
				if p.character not in char_map:
					char_map[p.character] = []
				char_map[p.character].append(p)
		
				if p.pronunciation not in pronon_map:
					pronon_map[p.pronunciation] = []
				pronon_map[p.pronunciation].append(p)
		self.char_map = char_map
		self.pronon_map = pronon_map
		# print len(char_map)
		# print len(pronon_map)

	def choose_one(self, plist,in_str):
		for p in plist:
			if p.use_cases:
				for u in p.use_cases:
					if "(" in u:
						i = u.index("(")
						u = u[0:i]
					if u in in_str:
						return p
		return plist[0]

	def get_notations(self, in_str):
		rlist = []
		for c in in_str:
			# print c.encode("utf-8")
			plist = self.char_map.get(c)
			if plist:
				if len(plist) == 1:
					rlist.append(plist[0].pronunciation)
				else:
					bestp = self.choose_one(plist,in_str)
					rlist.append(bestp.pronunciation)
			else:
				rlist.append(None)
		return rlist

	def get_notations_result(self, in_str):
		plist = self.get_notations(in_str)
		return NotationResult(in_str,plist)

	def get_pronunciations(self, character):
		return self.char_map.get(character,None)

	def get_pronunciations_result(self, character):
		plist = self.get_pronunciations(character)
		if plist:
			return PronunciationsResult(character, plist)
		else:
			return None

	def get_characters(self, pronunciation):
		return self.pronon_map.get(pronunciation, None)

	def get_characters_result(self,pronunciation):
		plist = self.get_characters(pronunciation)
		if plist:
			# for p in plist:
			# 	print p
			return CharactersResult(pronunciation,plist)
		else:
			return None

_default = NotationAdder(path.join(_here, "data.txt"))

def get_notations_result(in_str):
	return _default.get_notations_result(in_str)

def get_pronunciations_result(character):
	return _default.get_pronunciations_result(character)

def get_characters_result(pronunciation):
	return _default.get_characters_result(pronunciation)


if __name__ == '__main__':
	# import sys
	# reload(sys)
	# sys.setdefaultencoding("utf-8")
	# print len(_default.char_map)
	in_str = u"wo我唔钟意你"
	r = get_notations_result(in_str)
	print(r)

	print("")
	r = get_pronunciations_result(u"中")
	print(r)

	print 
	r = get_characters_result("zung1")
	print(r)
