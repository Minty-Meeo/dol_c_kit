from enum import Enum

# Massive thank you to these two documents:
# https://itanium-cxx-abi.github.io/cxx-abi/abi.html#mangling
# https://github.com/gchatelet/gcc_cpp_mangling_documentation

# Mutable String class

class MutableString(list):
	def __init__(self, string):
		for char in string:
			self.append(char)
	
	def __str__(self):
		return "".join(char for char in self)
	
	def pop_front(self, num):
		ret = ""
		for i in range(num):
			ret += self.pop(0)
		return ret
	
	def pop_back(self, num):
		ret = ""
		for i in range(num):
			ret += self.pop()
		return ret
	
	def startswith(self, string):
		return str(self).startswith(string)

# Simple Token class

class SyntaxToken(str):
	def __init__(self, string):
		self = string
	
	def itanium_mangle(self, compressibles):
		return "{}{}".format(len(self), self)

# Special Tokens

class SpecialTokenCtor(object):
	def __init__(self, num = 1):
		self.num = num
	def __str__(self):
		return "$$ctor{}".format(self.num)
	def __repr__(self):
		return "\'$$ctor{}\'".format(self.num)
	def itanium_mangle(self, compressibles):
		return "C{}".format(self.num)

class SpecialTokenDtor(object):
	def __init__(self, num = 1):
		self.num = num
	def __str__(self):
		return "$$dtor{}".format(self.num)
	def __repr__(self):
		return "\'$$dtor{}\'".format(self.num)
	def itanium_mangle(self, compressibles):
		return "D{}".format(self.num)

class SpecialTokenVTable(object):
	def __str__(self):
		return "$$vtable"
	def __repr__(self):
		return "\'$$vtable\'"
	def itanium_mangle(self, compressibles):
		return "TV"

class SpecialTokenRTTI(object):
	def __str__(self):
		return "$$rtti"
	def __repr__(self):
		return "\'$$rtti\'"
	def itanium_mangle(self, compressibles):
		return "TI"

class SpecialTokenVTTStructure(object): # Itanium exclusive?
	def __str__(self):
		return "$$vtt_structure"
	def __repr__(self):
		return "\'$$vtt_structure\'"
	def itanium_mangle(self, compressibles):
		return "TT"

class SpecialTokenRTTIName(object): # Itanium exclusive?
	def __str__(self):
		return "$$rtti_name"
	def __repr__(self):
		return "\'$$rtti_name\'"
	def itanium_mangle(self, compressibles):
		return "TS"

class SpecialTokenUnary(object):   # This one is extra special.  It should never be mangled, only provide context and be removed.
	def __str__(self):
		return "$$unary"
	def __repr__(self):
		return "\'$$unary\'"

# Special Tokens (operator overrides)

class SpecialOperatorNew(object):
	def __str__(self):
		return "operator new"
	def __repr__(self):
		return "\'operator new\'"
	def itanium_mangle(self, compressibles):
		return "nw"

class SpecialOperatorNewArray(object):
	def __str__(self):
		return "operator new[]"
	def __repr__(self):
		return "\'operator new[]\'"
	def itanium_mangle(self, compressibles):
		return "na"

class SpecialOperatorDelete(object):
	def __str__(self):
		return "operator delete"
	def __repr__(self):
		return "\'operator delete\'"
	def itanium_mangle(self, compressibles):
		return "dl"

class SpecialOperatorDeleteArray(object):
	def __str__(self):
		return "operator delete[]"
	def __repr__(self):
		return "\'operator delete[]\'"
	def itanium_mangle(self, compressibles):
		return "da"

class SpecialOperatorCoAwait(object):
	def __str__(self):
		return "operator co_await"
	def __repr__(self):
		return "\'operator co_await\'"
	def itanium_mangle(self, compressibles):
		return "aw"

class SpecialOperatorPositive(object):   # unary
	def __str__(self):
		return "operator + (unary)"
	def __repr__(self):
		return "\'operator + (unary)\'"
	def itanium_mangle(self, compressibles):
		return "ps"

class SpecialOperatorNegative(object):   # unary
	def __str__(self):
		return "operator - (unary)"
	def __repr__(self):
		return "\'operator - (unary)\'"
	def itanium_mangle(self, compressibles):
		return "ng"

class SpecialOperatorReference(object):   # unary
	def __str__(self):
		return "operator & (unary)"
	def __repr__(self):
		return "\'operator & (unary)\'"
	def itanium_mangle(self, compressibles):
		return "ad"   # address of

class SpecialOperatorDereference(object):   # unary
	def __str__(self):
		return "operator * (unary)"
	def __repr__(self):
		return "\'operator * (unary)\'"
	def itanium_mangle(self, compressibles):
		return "de"

class SpecialOperatorBitwiseNOT(object):
	def __str__(self):
		return "operator ~"
	def __repr__(self):
		return "\'operator ~\'"
	def itanium_mangle(self, compressibles):
		return "co"

class SpecialOperatorAdd(object):
	def __str__(self):
		return "operator +"
	def __repr__(self):
		return "\'operator +\'"
	def itanium_mangle(self, compressibles):
		return "pl"

class SpecialOperatorSubtract(object):
	def __str__(self):
		return "operator -"
	def __repr__(self):
		return "\'operator -\'"
	def itanium_mangle(self, compressibles):
		return "mi"

class SpecialOperatorMultiply(object):
	def __str__(self):
		return "operator *"
	def __repr__(self):
		return "\'operator *\'"
	def itanium_mangle(self, compressibles):
		return "ml"

class SpecialOperatorDivide(object):
	def __str__(self):
		return "operator /"
	def __repr__(self):
		return "\'operator /\'"
	def itanium_mangle(self, compressibles):
		return "dv"

class SpecialOperatorModulo(object):
	def __str__(self):
		return "operator %"
	def __repr__(self):
		return "\'operator %\'"
	def itanium_mangle(self, compressibles):
		return "rm"   # remainder

class SpecialOperatorBitwiseAND(object):
	def __str__(self):
		return "operator &"
	def __repr__(self):
		return "\'operator &\'"
	def itanium_mangle(self, compressibles):
		return "an"

class SpecialOperatorBitwiseOR(object):
	def __str__(self):
		return "operator |"
	def __repr__(self):
		return "\'operator |\'"
	def itanium_mangle(self, compressibles):
		return "or"

class SpecialOperatorBitwiseXOR(object):
	def __str__(self):
		return "operator ^"
	def __repr__(self):
		return "\'operator ^\'"
	def itanium_mangle(self, compressibles):
		return "eo"   # exclusive or

class SpecialOperatorAssign(object):
	def __str__(self):
		return "operator ="
	def __repr__(self):
		return "\'operator =\'"
	def itanium_mangle(self, compressibles):
		return "aS"

class SpecialOperatorAssignAdd(object):
	def __str__(self):
		return "operator +="
	def __repr__(self):
		return "\'operator +=\'"
	def itanium_mangle(self, compressibles):
		return "pL"

class SpecialOperatorAssignSubtract(object):
	def __str__(self):
		return "operator -="
	def __repr__(self):
		return "\'operator -=\'"
	def itanium_mangle(self, compressibles):
		return "mI"

class SpecialOperatorAssignMultiply(object):
	def __str__(self):
		return "operator *="
	def __repr__(self):
		return "\'operator *=\'"
	def itanium_mangle(self, compressibles):
		return "mL"

class SpecialOperatorAssignDivide(object):
	def __str__(self):
		return "operator /="
	def __repr__(self):
		return "\'operator /=\'"
	def itanium_mangle(self, compressibles):
		return "dV"

class SpecialOperatorAssignModulo(object):
	def __str__(self):
		return "operator &="
	def __repr__(self):
		return "\'operator &=\'"
	def itanium_mangle(self, compressibles):
		return "rM"   # remainder

class SpecialOperatorAssignBitwiseAND(object):
	def __str__(self):
		return "operator &="
	def __repr__(self):
		return "\'operator &=\'"
	def itanium_mangle(self, compressibles):
		return "aN"

class SpecialOperatorAssignBitwiseOR(object):
	def __str__(self):
		return "operator |="
	def __repr__(self):
		return "\'operator |=\'"
	def itanium_mangle(self, compressibles):
		return "oR"

class SpecialOperatorAssignBitwiseXOR(object):
	def __str__(self):
		return "operator ^="
	def __repr__(self):
		return "\'operator ^=\'"
	def itanium_mangle(self, compressibles):
		return "eO"   # exclusive or

class SpecialOperatorLeftShift(object):
	def __str__(self):
		return "operator <<"
	def __repr__(self):
		return "\'operator <<\'"
	def itanium_mangle(self, compressibles):
		return "ls"

class SpecialOperatorRightShift(object):
	def __str__(self):
		return "operator >>"
	def __repr__(self):
		return "\'operator >>\'"
	def itanium_mangle(self, compressibles):
		return "rs"

class SpecialOperatorAssignLeftShift(object):
	def __str__(self):
		return "operator <<="
	def __repr__(self):
		return "\'operator <<=\'"
	def itanium_mangle(self, compressibles):
		return "lS"

class SpecialOperatorAssignRightShift(object):
	def __str__(self):
		return "operator >>="
	def __repr__(self):
		return "\'operator >>=\'"
	def itanium_mangle(self, compressibles):
		return "rS"

class SpecialOperatorEqual(object):
	def __str__(self):
		return "operator =="
	def __repr__(self):
		return "\'operator ==\'"
	def itanium_mangle(self, compressibles):
		return "eq"

class SpecialOperatorNotEqual(object):
	def __str__(self):
		return "operator !="
	def __repr__(self):
		return "\'operator !=\'"
	def itanium_mangle(self, compressibles):
		return "ne"

class SpecialOperatorLesserThan(object):
	def __str__(self):
		return "operator <"
	def __repr__(self):
		return "\'operator <\'"
	def itanium_mangle(self, compressibles):
		return "lt"

class SpecialOperatorGreaterThan(object):
	def __str__(self):
		return "operator >"
	def __repr__(self):
		return "\'operator >\'"
	def itanium_mangle(self, compressibles):
		return "gt"

class SpecialOperatorLesserThanOrEqual(object):
	def __str__(self):
		return "operator <="
	def __repr__(self):
		return "\'operator <=\'"
	def itanium_mangle(self, compressibles):
		return "le"

class SpecialOperatorGreaterThanOrEqual(object):
	def __str__(self):
		return "operator >="
	def __repr__(self):
		return "\'operator >=\'"
	def itanium_mangle(self, compressibles):
		return "ge"

class SpecialOperatorSpaceShip(object):
	def __str__(self):
		return "operator <=>"
	def __repr__(self):
		return "\'operator <=>\'"
	def itanium_mangle(self, compressibles):
		return "ss"

class SpecialOperatorLogicalNOT(object):
	def __str__(self):
		return "operator !"
	def __repr__(self):
		return "\'operator !\'"
	def itanium_mangle(self, compressibles):
		return "nt"

class SpecialOperatorLogicalAND(object):
	def __str__(self):
		return "operator &&"
	def __repr__(self):
		return "\'operator &&\'"
	def itanium_mangle(self, compressibles):
		return "aa"

class SpecialOperatorLogicalOR(object):
	def __str__(self):
		return "operator ||"
	def __repr__(self):
		return "\'operator ||\'"
	def itanium_mangle(self, compressibles):
		return "oo"

class SpecialOperatorIncrement(object):
	def __str__(self):
		return "operator ++"
	def __repr__(self):
		return "\'operator ++\'"
	def itanium_mangle(self, compressibles):
		return "pp"

class SpecialOperatorDecrement(object):
	def __str__(self):
		return "operator --"
	def __repr__(self):
		return "\'operator --\'"
	def itanium_mangle(self, compressibles):
		return "mm"

class SpecialOperatorArraySubscript(object):
	def __str__(self):
		return "operator []"
	def __repr__(self):
		return "\'operator []\'"
	def itanium_mangle(self, compressibles):
		return "ix"

# There are a few more operator overrides but I genuinely don't understand them.  I'm sorry.

# Built-in types

class BuiltinVoid(object):
	def __str__(self):
		return "void"
	def __repr__(self):
		return "\'void\'"
	def itanium_mangle(self, compressibles):
		return "v"

class BuiltinBool(object):
	def __str__(self):
		return "bool"
	def __repr__(self):
		return "\'bool\'"
	def itanium_mangle(self, compressibles):
		return "b"

class BuiltinChar(object):
	def __str__(self):
		return "char"
	def __repr__(self):
		return "\'char\'"
	def itanium_mangle(self, compressibles):
		return "c"

class BuiltinShort(object):
	def __str__(self):
		return "short"
	def __repr__(self):
		return "\'short\'"
	def itanium_mangle(self, compressibles):
		return "s"

class BuiltinInt(object):
	def __str__(self):
		return "int"
	def __repr__(self):
		return "\'int\'"
	def itanium_mangle(self, compressibles):
		return "i"

class Builtin__int64(object):
	def __str__(self):
		return "__int64"
	def __repr__(self):
		return "\'__int64\'"
	def itanium_mangle(self, compressibles):
		return "x"

class Builtin__int128(object):
	def __str__(self):
		return "__int128"
	def __repr__(self):
		return "\'__int128\'"
	def itanium_mangle(self, compressibles):
		return "n"

class BuiltinFloat(object):
	def __str__(self):
		return "float"
	def __repr__(self):
		return "\'float\'"
	def itanium_mangle(self, compressibles):
		return "f"

class BuiltinDouble(object):
	def __str__(self):
		return "double"
	def __repr__(self):
		return "\'double\'"
	def itanium_mangle(self, compressibles):
		return "d"

class Builtin__float80(object):
	def __str__(self):
		return "__float80"
	def __repr__(self):
		return "\'__float80\'"
	def itanium_mangle(self, compressibles):
		return "e"

class Builtin__float128(object):
	def __str__(self):
		return "__float128"
	def __repr__(self):
		return "\'__float128\'"
	def itanium_mangle(self, compressibles):
		return "g"

class BuiltinEllipses(object):
	def __str__(self):
		return "..."
	def __repr__(self):
		return "\'...\'"
	def itanium_mangle(self, compressibles):
		return "z"

# Decorator Classes

class OperatorUnsigned(object):
	def __init__(self):
		self.rhand = None
	
	def __str__(self):
		return "unsigned {}".format(self.rhand)
	def __repr__(self):
		return "\'unsigned\' {}".format(repr(self.rhand))
	
	def itanium_mangle(self, compressibles):
		rhand_symbol = self.rhand.itanium_mangle(compressibles)
		if rhand_symbol == "c":   # char
			return "h"
		if rhand_symbol == "s":   # short
			return "t"
		if rhand_symbol == "i":   # int
			return "j"
		if rhand_symbol == "l":   # long int
			return "m"
		if rhand_symbol == "x":   # long long int
			return "y"
		if rhand_symbol == "n":    # __int128
			return "o"
		raise Exception("Type {} is incompatible with unsigned decorator!".format(rhand_symbol))

class OperatorSigned(object):
	def __init__(self):
		self.rhand = None
	
	def __str__(self):
		return "signed {}".format(self.rhand)
	def __repr__(self):
		return "\'signed\' {}".format(repr(self.rhand))
	
	def itanium_mangle(self, compressibles):
		rhand_symbol = self.rhand.itanium_mangle(compressibles)
		if rhand_symbol == "c":   # char
			return "a"
		if rhand_symbol == "s":   # short
			return "s"
		if rhand_symbol == "i":   # int
			return "i"
		if rhand_symbol == "l":   # long int
			return "l"
		if rhand_symbol == "x":   # long long int
			return "x"
		if rhand_symbol == "n":    # __int128
			return "n"
		raise Exception("Type {} is incompatible with signed decorator!".format(rhand_symbol))

class OperatorLong(object):
	def __init__(self):
		self.rhand = None
	
	def __str__(self):
		return "long {}".format(self.rhand)
	def __repr__(self):
		return "\'long\' {}".format(repr(self.rhand))
	
	def itanium_mangle(self, compressibles):
		rhand_symbol = self.rhand.itanium_mangle(compressibles)
		if rhand_symbol == "i":   # int
			return "l"
		if rhand_symbol == "l":   # long int
			return "x"
		if rhand_symbol == "d":   # double
			return "e"
		raise Exception("Type {} is incompatible with long decorator!".format(rhand_symbol))

class OperatorConst(object):
	def __init__(self):
		self.lhand = None
	
	def __str__(self):
		return "{} const".format(self.lhand)
	def __repr__(self):
		return "{} \'const\'".format(repr(self.lhand))
	
	def itanium_mangle(self, compressibles):
		key = str(self.lhand)
		if key in compressibles:
			lhand_symbol = compressibles[key]
		else:
			lhand_symbol = self.lhand.itanium_mangle(compressibles)
			if type(self.lhand) not in builtin_types:
				compressibles.register(key)
		
		# Constness does not matter until indirection happens
		return lhand_symbol

class OperatorPointer(object):
	def __init__(self):
		self.lhand = None
	
	def __str__(self):
		return "{} *".format(self.lhand)
	def __repr__(self):
		return "{} \'*\'".format(repr(self.lhand))
	
	def itanium_mangle(self, compressibles):
		key = str(self.lhand)
		if key in compressibles:
			lhand_symbol = compressibles[key]
		else:
			lhand_symbol = self.lhand.itanium_mangle(compressibles)
			if type(self.lhand) not in builtin_types:
				compressibles.register(key)
		
		if type(self.lhand) == OperatorConst:
			return "PK{}".format(lhand_symbol)
		else:
			return "P{}".format(lhand_symbol)

class OperatorReference(object):
	def __init__(self):
		self.lhand = None
	
	def __str__(self):
		return "{} &".format(self.lhand)
	def __repr__(self):
		return "{} \'&\'".format(repr(self.lhand))
	
	def itanium_mangle(self, compressibles):
		key = str(self.lhand)
		if key in compressibles:
			lhand_symbol = compressibles[key]
		else:
			lhand_symbol = self.lhand.itanium_mangle(compressibles)
			if type(self.lhand) not in builtin_types:
				compressibles.register(key)
		
		if type(self.lhand) == OperatorConst:
			return "RK{}".format(lhand_symbol)
		else:
			return "R{}".format(lhand_symbol)

class OperatorRHandReference(object):
	def __init__(self):
		self.lhand = None
	
	def __str__(self):
		return "{} &&".format(self.lhand)
	def __repr__(self):
		return "{} \'&&\'".format(repr(self.lhand))
	
	def itanium_mangle(self, compressibles):
		key = str(self.lhand)
		if key in compressibles:
			lhand_symbol = compressibles[key]
		else:
			lhand_symbol = self.lhand.itanium_mangle(compressibles)
			if type(self.lhand) not in builtin_types:
				compressibles.register(key)
		
		if type(self.lhand) == OperatorConst:
			return "OK{}".format(lhand_symbol)
		else:
			return "O{}".format(lhand_symbol)

# Complex Classes

class OperatorNamespace(object):
	def __init__(self):
		self.lhand = None
		self.rhand = None
	
	def __str__(self):
		return "{} :: {}".format(self.lhand, self.rhand)
	def __repr__(self):
		return "{} \'::\' {}".format(repr(self.lhand), repr(self.rhand))
	
	def itanium_mangle(self, compressibles):
		if self.lhand == "std":
			return "St" + self.rhand.itanium_mangle(compressibles)
		if type(self.rhand) == SpecialTokenVTable \
		or type(self.rhand) == SpecialTokenRTTI \
		or type(self.rhand) == SpecialTokenVTTStructure \
		or type(self.rhand) == SpecialTokenRTTIName:
			return self.rhand.itanium_mangle(compressibles) + self.lhand.itanium_mangle(compressibles) # I hate this dirty hack
		return "N" + self.itanium_mangle_ns(compressibles) + "E"
	
	def itanium_mangle_ns(self, compressibles):
		key = str(self.lhand)
		if key in compressibles:
			return compressibles[key] + self.rhand.itanium_mangle(compressibles)
		else:
			if type(self.lhand) == OperatorNamespace:
				lhand_symbol = self.lhand.itanium_mangle_ns(compressibles)
				if type(self.lhand) not in builtin_types:
					compressibles.register(key)
				rhand_symbol = self.rhand.itanium_mangle(compressibles)
			else:
				lhand_symbol = self.lhand.itanium_mangle(compressibles)
				if type(self.lhand) not in builtin_types:
					compressibles.register(key)
				rhand_symbol = self.rhand.itanium_mangle(compressibles)
			return lhand_symbol + rhand_symbol

class OperatorTemplateArgs(list):
	def __init__(self, mutstring):
		self.lhand = None
		
		mutstring.pop(0)
		while mutstring:
			char = mutstring[0]
			if char in whitespace:
				mutstring.pop(0)
				continue
			if char == ',':
				mutstring.pop(0)
				continue
			if char == ')':
				raise Exception("\')\' was unexpected at this time.")
			if char == '>':
				mutstring.pop(0)
				if not self:
					raise Exception("TODO: what is the behavior for empty template arguments?")
				return
			self.append(Expression(mutstring)[0])
		raise Exception("No closing brace found!")
	
	def __str__(self):
		return "{} < {} >".format(self.lhand, ", ".join(str(iter) for iter in self))
	def __hash__(self):
		return hash((tuple(self), self.lhand))
	
	def itanium_mangle(self, compressibles):
		# Lefthand mangles first
		key = str(self.lhand)
		if key in compressibles:
			lhand_symbol = compressibles[key]
		else:
			lhand_symbol = self.lhand.itanium_mangle(compressibles)
			if type(self.lhand) not in builtin_types:
				compressibles.register(key)
		
		# Arguments mangle second
		args = ""
		for iter in self:
			key = str(iter)
			if key in compressibles:
				args += compressibles[key]
			else:
				args += iter.itanium_mangle(compressibles)
				if type(iter) not in builtin_types:
					compressibles.register(key)
		
		# Finally, the entire thing mangles third
		key = str(self)
		if key in compressibles:
			return compressibles[key]
		compressibles.register(key)
		
		return "{}I{}E".format(lhand_symbol, args)

class OperatorFunctionArgs(list):
	def __init__(self, mutstring):
		mutstring.pop(0)
		while mutstring:
			char = mutstring[0]
			if char in whitespace:
				mutstring.pop(0)
				continue
			if char == ',':
				mutstring.pop(0)
				continue
			if char == ')':
				mutstring.pop(0)
				if not self:
					self.append(BuiltinVoid())
				return
			if char == '>':
				raise Exception("\'>\' was unexpected at this time.")
			self.append(Expression(mutstring)[0])
		raise Exception("No closing brace found!")
	
	def __str__(self):
		return "( {} )".format(", ".join(str(iter) for iter in self))
	
	def itanium_mangle(self, compressibles):
		args = ""
		for iter in self:
			key = str(iter)
			if key in compressibles:
				args += compressibles[key]
			else:
				args += iter.itanium_mangle(compressibles)
				if type(iter) not in builtin_types:
					compressibles.register(key)
		return args

class Expression(list):
	def __init__(self, mutstring = None):
		while mutstring:
			if mutstring[0] in whitespace:
				mutstring.pop(0)
				continue
			
			# Operators (and ellipses because idk how else to parse them)
			if mutstring.startswith("*"):
				mutstring.pop_front(1)
				self.append(OperatorPointer())
				continue
			if mutstring.startswith("&&"):
				mutstring.pop_front(2)
				self.append(OperatorRHandReference())
				continue
			if mutstring.startswith("&"):
				mutstring.pop_front(1)
				self.append(OperatorReference())
				continue
			if mutstring.startswith("::"):
				mutstring.pop_front(2)
				self.append(OperatorNamespace())
				continue
			if mutstring.startswith("..."):
				mutstring.pop_front(3)
				self.append(BuiltinEllipses())
				continue
			
			# Argument Lists
			char = mutstring[0]
			if char == '(':
				self.append(OperatorFunctionArgs(mutstring))
				continue
			if char == '<':
				self.append(OperatorTemplateArgs(mutstring))
				continue
			if char == ")" \
			or char == ">" \
			or char == ",":
				break
			
			# Get a string
			curr_string = ""
			while mutstring:
				if mutstring[0] not in alphanumeric and mutstring[0] != '$':   # '$' is for special tokens
					break
				curr_string += mutstring.pop(0)
			
			# const, unsigned, signed, long
			# plus, built-in types and a redundant ellipses check
			if \
			( self.append(OperatorConst())    ,) if curr_string == "const"      else \
			( self.append(OperatorUnsigned()) ,) if curr_string == "unsigned"   else \
			( self.append(OperatorSigned())   ,) if curr_string == "signed"     else \
			( self.append(OperatorLong())     ,) if curr_string == "long"       else \
			( self.append(BuiltinVoid())      ,) if curr_string == "void"       else \
			( self.append(BuiltinBool())      ,) if curr_string == "bool"       else \
			( self.append(BuiltinChar())      ,) if curr_string == "char"       else \
			( self.append(BuiltinShort())     ,) if curr_string == "short"      else \
			( self.append(BuiltinInt())       ,) if curr_string == "int"        else \
			( self.append(Builtin__int64())   ,) if curr_string == "__int64"    else \
			( self.append(Builtin__int128())  ,) if curr_string == "__int128"   else \
			( self.append(BuiltinFloat())     ,) if curr_string == "float"      else \
			( self.append(BuiltinDouble())    ,) if curr_string == "double"     else \
			( self.append(Builtin__float80()) ,) if curr_string == "__float80"  else \
			( self.append(Builtin__float128()),) if curr_string == "__float128" else \
			( self.append(BuiltinEllipses())  ,) if curr_string == "..."        else ():
				continue
			
			# SpecialTokens
			if \
			( self.append(SpecialTokenUnary())       ,) if curr_string == "$$unary"         else \
			( self.append(SpecialTokenCtor())        ,) if curr_string == "$$ctor"          else \
			( self.append(SpecialTokenCtor(1))       ,) if curr_string == "$$ctor1"         else \
			( self.append(SpecialTokenCtor(2))       ,) if curr_string == "$$ctor2"         else \
			( self.append(SpecialTokenCtor(3))       ,) if curr_string == "$$ctor3"         else \
			( self.append(SpecialTokenDtor())        ,) if curr_string == "$$dtor"          else \
			( self.append(SpecialTokenDtor(0))       ,) if curr_string == "$$dtor0"         else \
			( self.append(SpecialTokenDtor(1))       ,) if curr_string == "$$dtor1"         else \
			( self.append(SpecialTokenDtor(2))       ,) if curr_string == "$$dtor2"         else \
			( self.append(SpecialTokenVTable())      ,) if curr_string == "$$vtable"        else \
			( self.append(SpecialTokenRTTI())        ,) if curr_string == "$$rtti"          else \
			( self.append(SpecialTokenVTTStructure()),) if curr_string == "$$vtt_structure" else \
			( self.append(SpecialTokenRTTIName())    ,) if curr_string == "$$rtti_name"     else ():
				continue
			
			# Operator overrides (are complicated)
			if curr_string == "operator":
				while mutstring[0] in whitespace:
					mutstring.pop(0)
				
				# Non-alphanumeric operators.  Also, this is a grotesque use of the ternary operator, tuples, and line continuations.
				if \
				( mutstring.pop_front(3), self.append(SpecialOperatorAssignLeftShift())    ) if mutstring.startswith("<<=") else \
				( mutstring.pop_front(3), self.append(SpecialOperatorAssignRightShift())   ) if mutstring.startswith(">>=") else \
				( mutstring.pop_front(3), self.append(SpecialOperatorSpaceShip())          ) if mutstring.startswith("<=>") else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignAdd())          ) if mutstring.startswith("+=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignSubtract())     ) if mutstring.startswith("-=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignMultiply())     ) if mutstring.startswith("*=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignDivide())       ) if mutstring.startswith("/=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignModulo())       ) if mutstring.startswith("%=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignBitwiseAND())   ) if mutstring.startswith("&=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignBitwiseOR())    ) if mutstring.startswith("|=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorAssignBitwiseXOR())   ) if mutstring.startswith("^=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorLeftShift())          ) if mutstring.startswith("<<")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorRightShift())         ) if mutstring.startswith(">>")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorEqual())              ) if mutstring.startswith("==")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorNotEqual())           ) if mutstring.startswith("!=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorLesserThanOrEqual())  ) if mutstring.startswith("<=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorGreaterThanOrEqual()) ) if mutstring.startswith(">=")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorLogicalAND())         ) if mutstring.startswith("&&")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorLogicalOR())          ) if mutstring.startswith("||")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorIncrement())          ) if mutstring.startswith("++")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorDecrement())          ) if mutstring.startswith("--")  else \
				( mutstring.pop_front(2), self.append(SpecialOperatorArraySubscript())     ) if mutstring.startswith("[]")  else \
				( mutstring.pop_front(1), self.append(SpecialOperatorBitwiseNOT())         ) if mutstring.startswith("~")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorAdd())                ) if mutstring.startswith("+")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorSubtract())           ) if mutstring.startswith("-")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorMultiply())           ) if mutstring.startswith("*")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorDivide())             ) if mutstring.startswith("/")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorModulo())             ) if mutstring.startswith("%")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorBitwiseAND())         ) if mutstring.startswith("&")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorBitwiseOR())          ) if mutstring.startswith("|")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorBitwiseXOR())         ) if mutstring.startswith("^")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorAssign())             ) if mutstring.startswith("=")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorLesserThan())         ) if mutstring.startswith("<")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorGreaterThan())        ) if mutstring.startswith(">")   else \
				( mutstring.pop_front(1), self.append(SpecialOperatorLogicalNOT())         ) if mutstring.startswith("!")   else ():
					continue
				
				# new, delete, new[], delete[], and co_await
				curr_string = ""
				while mutstring:
					if mutstring[0] not in alphanumeric and mutstring[0] != '$':   # '$' is for special tokens
						break
					curr_string += mutstring.pop(0)
				if curr_string == "new":
					while mutstring[0] in whitespace:
						mutstring.pop(0)
					( mutstring.pop_front(2), self.append(SpecialOperatorNewArray()) ) if mutstring.startswith("[]") else self.append(SpecialOperatorNew())
					continue
				if curr_string == "delete":
					while mutstring[0] in whitespace:
						mutstring.pop(0)
					( mutstring.pop_front(2), self.append(SpecialOperatorDeleteArray()) ) if mutstring.startswith("[]") else self.append(SpecialOperatorDelete())
					continue
				if curr_string == "co_await":
					self.append(SpecialOperatorCoAwait())
					continue
				# uh oh
				raise Exception("Special operator parsing failed!")
			
			if curr_string:
				self.append(SyntaxToken(curr_string))
				continue
			else:
				raise Exception("Expression parsing failed!")
#		print(self)   # uncomment this to see the expression before operator resolving
		# Order of Operations
		i = 0
		while i < len(self):
			iter = self[i]
			if type(iter) == OperatorTemplateArgs:
				iter.lhand = self.pop(i-1)
				continue
			if type(iter) == SpecialOperatorArraySubscript:
				iter.lhand = self.pop(i-1)
				continue
			i += 1
			continue
		i = 0
		while i < len(self):
			iter = self[i]
			if type(iter) == OperatorNamespace:
				iter.rhand = self.pop(i+1)
				iter.lhand = self.pop(i-1)
				continue
			if type(iter) == SpecialTokenUnary:
				if type(self[i-1]) == SpecialOperatorAdd:
					self[i-1] = SpecialOperatorPositive()
					self.pop(i)
					continue
				if type(self[i-1]) == SpecialOperatorSubtract:
					self[i-1] = SpecialOperatorNegative()
					self.pop(i)
					continue
				if type(self[i-1]) == SpecialOperatorBitwiseAND:
					self[i-1] = SpecialOperatorReference()
					self.pop(i)
					continue
				if type(self[i-1]) == SpecialOperatorMultiply:
					self[i-1] = SpecialOperatorDereference()
					self.pop(i)
					continue
				raise Exception("Special Token \"$$unary\" can't be used for this!")
			i += 1
			continue
		i = len(self) - 1
		while i >= 0:
			iter = self[i]
			if type(iter) == OperatorLong:
				iter.rhand = self.pop(i+1)
			if type(iter) == OperatorUnsigned:
				iter.rhand = self.pop(i+1)
			if type(iter) == OperatorSigned:
				iter.rhand = self.pop(i+1)
			i -= 1
		i = 0
		while i < len(self):
			iter = self[i]
			if type(iter) == OperatorPointer:
				iter.lhand = self.pop(i-1)
				continue
			if type(iter) == OperatorReference:
				iter.lhand = self.pop(i-1)
				continue
			if type(iter) == OperatorRHandReference:
				iter.lhand = self.pop(i-1)
				continue
			if type(iter) == OperatorConst:
				if type(self[i-1]) == OperatorReference:
					raise Exception("\'const\' qualifiers cannot be applied to references")
				if type(self[i-1]) == OperatorConst:
					raise Exception("Duplicate \'const\' qualifiers")
				iter.lhand = self.pop(i-1)
				continue
			i += 1
			continue
	
	def __str__(self):
		return " ".join(str(iter) for iter in self)

class Signature(Expression):
	def itanium_mangle(self, compressibles = None):
		if compressibles == None: # This is for debugging only
			compressibles = ItaniumSymbolDictionary()
		
		if len(self) == 0:
			return ""
		if len(self) == 1:
			# Special signature (vtable, rtti, etc.)
			return "_Z" + self[0].itanium_mangle(compressibles)
		if len(self) == 2:
			# Special function signature (ctors and dtors)
			if type(self[1]) == OperatorFunctionArgs \
			or type(self[1]) == OperatorConst and type(self[1].lhand) == OperatorFunctionArgs:
				name = self[0].itanium_mangle(compressibles)
				args = self[1].itanium_mangle(compressibles)
				return "_Z" + name + args
			# Global variable signature
			else:
				name = self[1].itanium_mangle(compressibles)
				if type(self[0]) == OperatorConst and type(self[0].lhand) in indirection_decorators:
					name = "L" + name
				return "_Z" + name
		if len(self) == 3:
			# Function signature
			if type(self[2]) == OperatorFunctionArgs:
				name = self[1].itanium_mangle(compressibles)
				args = self[2].itanium_mangle(compressibles)
				return "_Z" + name + args
			# Const class methods
			if type(self[2]) == OperatorConst and type(self[2].lhand) == OperatorFunctionArgs:
				name = "NK" + self[1].itanium_mangle_ns(compressibles) + "E"   # This will always be a namespace, unless it is invalid C++.
				args = self[2].itanium_mangle(compressibles)
				return "_Z" + name + args
		raise Exception("Too much stuff!")


# Some stuff

alphanumeric = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0','_','~',)
whitespace = (' ', '	',)
builtin_types = (
	BuiltinVoid,
	BuiltinBool,
	BuiltinChar,
	BuiltinShort,
	BuiltinInt,
	Builtin__int64,
	Builtin__int128,
	BuiltinFloat,
	BuiltinDouble,
	Builtin__float80,
	Builtin__float128,
	BuiltinEllipses,
	OperatorUnsigned,
	OperatorSigned,
	OperatorLong,
)
indirection_decorators = (
	OperatorPointer,
	OperatorReference,
	OperatorRHandReference,
)

class ItaniumSymbolDictionary(dict):
	def __init__(self):
		self["std"] = "St"
		self["std :: nullptr_t"] = "Dn"
		self["std :: allocator"] = "Sa"
		self["std :: basic_string"] = "Sb"
		self["std :: basic_string < char, std :: char_traits < char >, std :: allocator < char > >"] = "Ss"
		self["std :: basic_istream < char, std :: char_traits < char > >"] = "Si"
		self["std :: basic_ostream < char, std :: char_traits < char > >"] = "So"
		self["std :: basic_iostream < char, std :: char_traits < char > >"] = "Sd"
		self.n = -1
	
	def __str__(self):
		for iter in self:
			return "\n".join("{} : {}".format(iter, self[iter]) for iter in self)
	
	base_36 = {
		0  : "0",
		1  : "1",
		2  : "2",
		3  : "3",
		4  : "4",
		5  : "5",
		6  : "6",
		7  : "7",
		8  : "8",
		9  : "9",
		10 : "A",
		11 : "B",
		12 : "C",
		13 : "D",
		14 : "E",
		15 : "F",
		16 : "G",
		17 : "H",
		18 : "I",
		19 : "J",
		20 : "K",
		21 : "L",
		22 : "M",
		23 : "N",
		24 : "O",
		25 : "P",
		26 : "Q",
		27 : "R",
		28 : "S",
		29 : "T",
		30 : "U",
		31 : "V",
		32 : "W",
		33 : "X",
		34 : "Y",
		35 : "Z"
	}
	
	def register(self, key):
		if key not in self:
			if self.n == -1:
				val = "S_"
				self.n = 0
			elif self.n == 0:
				val = "S0_"
				self.n = 1
			else:
				idx = self.n
				self.n += 1
				val = ""
				while idx > 0:
					val = ItaniumSymbolDictionary.base_36[idx % 36] + val
					idx //= 36
				val = "S" + val + "_"
			self[key] = val

# Accessible for external use

class ABI(Enum):
	Itanium = 0

class LDPlusPlus(object):
	def __init__(self, abi):
		self.buffer = ""
		self.abi = abi
	
	# https://sourceware.org/binutils/docs/ld/Simple-Assignments.html
	def assign(self, prototype, value):
		if self.abi == ABI.Itanium:
			self.buffer += "{} = {};\n".format(itanium_mangle(prototype), hex(value))
		else:
			raise Exception("Unsupported ABI!")
	
	# https://sourceware.org/binutils/docs/ld/PROVIDE.html
	def provide(self, prototype, value):
		if self.abi == ABI.Itanium:
			self.buffer += "PROVIDE({} = {});\n".format(itanium_mangle(prototype), hex(value))
		else:
			raise Exception("Unsupported ABI!")
	
	def save(self, filepath):
		try:
			with open(filepath, "w") as f:
				f.write(self.buffer)
		except OSError:
			print("Warning: \"{:s}\" could not be opened!".format(repr(filepath)[+1:-1]))

def mangle(prototype, abi):
	if abi == ABI.Itanium:
		return itanium_mangle(prototype, compressibles)
	else:
		raise Exception("Unsupported ABI!")

def itanium_mangle(prototype):
	return Signature(MutableString(prototype)).itanium_mangle()

# Some diagnostics
def diagnose(prototype, correct_mangled, verbose = False):
	compressibles = ItaniumSymbolDictionary()
	signature = Signature(MutableString(prototype))
	mangled = signature.itanium_mangle(compressibles)
	if verbose == True:
		print()
		print(compressibles)
	print("{:50s} {:30s} {} {:30s}".format(prototype, mangled, "==" if mangled == correct_mangled else "!=",correct_mangled))
#	print("{:50s} {:30s} {} {:30s}".format(str(signature), mangled, "==" if mangled == correct_mangled else "!=",correct_mangled))

if __name__ == "__main__":
	print("\nConst or nested variable declaration")
	diagnose("int* const bar", "_ZL3bar")
	diagnose("int a::bar", "_ZN1a3barE")
	diagnose("int std::bar", "_ZSt3bar")
	print("\nFunction declaration")
	diagnose("void foo()", "_Z3foov")
	print("\nDeclaration and user defined type encoding")
	diagnose("void a::S::foo()", "_ZN1a1S3fooEv")
	diagnose("void a::S::const_foo() const", "_ZNK1a1S9const_fooEv") # Const OperatorFunctionArgs are stupid
	print("\nSubstitutions")
	diagnose("void foo(void *, void *)", "_Z3fooPvS_")
	print("\nMore on substitutions in function parameters")
	diagnose("void foo(int)", "_Z3fooi")
	diagnose("void foo()", "_Z3foov")
	diagnose("void foo(void)", "_Z3foov")
	diagnose("void foo(char, int, short)", "_Z3foocis")
	print("\nIndirection decorators")
	diagnose("void foo(int)", "_Z3fooi")
	diagnose("void foo(int const)", "_Z3fooi")
	diagnose("void foo(int const *)", "_Z3fooPKi")
	diagnose("void foo(int const &)", "_Z3fooRKi")
	diagnose("void foo(int const * const *)", "_Z3fooPKPKi")
	diagnose("void foo(int * &)", "_Z3fooRPi")
	print("\nFunction pointers")
	print("--Massive TODO--")
	print("\nMore on substitutions in scopes")
	diagnose("void a::foo(a::A)", "_ZN1a3fooENS_1AE")
	diagnose("void std::foo(std::A)", "_ZSt3fooSt1A")
	diagnose("void A::foo(A::B)", "_ZN1A3fooENS_1BE") # Reduntant since classes are fancy namespaces
	print("\nMore on substitutions in templates")
	diagnose("void A<int>::foo(A<int>)", "_ZN1AIiE3fooES0_")
	diagnose("void A::foo<int>(int, int)", "_ZN1A3fooIiEEvT_S1_") # I don't understand this
	diagnose("void A<int>::foo(int, int)", "_ZN1AIiE3fooEii")
	diagnose("void A<B>::foo(B, B)", "_ZN1AI1BE3fooES0_S0_")
	diagnose("int foo(char, int, char)", "_Z3fooIicET_T0_S0_S1_") # weird shit with function templates that would break the mangler as-is
	diagnose("int foo(int, int, int)", "_Z3fooIiiET_T0_S0_S1_") # ditto
	print("\nctors and dtors")
	diagnose("ClassA::$$ctor()", "_ZN6ClassAC1Ev")
	diagnose("ClassA::$$ctor1()", "_ZN6ClassAC1Ev")
	diagnose("ClassA::$$ctor2()", "_ZN6ClassAC2Ev")
	diagnose("ClassA::$$ctor3()", "_ZN6ClassAC3Ev")
	diagnose("ClassA::$$dtor()", "_ZN6ClassAD1Ev")
	diagnose("ClassA::$$dtor0()", "_ZN6ClassAD0Ev")
	diagnose("ClassA::$$dtor1()", "_ZN6ClassAD1Ev")
	diagnose("ClassA::$$dtor2()", "_ZN6ClassAD2Ev")
	print("\nvtables and rtti")
	diagnose("ClassA::$$vtable", "_ZTV6ClassA")
	diagnose("NamespaceA::ClassA::$$vtable", "_ZTVN10NamespaceA6ClassAE")
	diagnose("ClassA::$$vtt_structure", "?")
	diagnose("ClassA::$$rtti", "?")
	diagnose("ClassA::$$rtti_name", "?")
	print("\noperator overloads")
	diagnose("void* operator new(unsigned int)", "_Znwj")
	diagnose("void* operator new[](unsigned int)", "_Znaj")
	diagnose("void operator +(unsigned int)", "?")
	diagnose("void operator + $$unary(unsigned int)", "?")
	diagnose("void operator <=>(unsigned int)", "?")
	diagnose("void operator >>=(unsigned int)", "?")
	diagnose("void myclass::operator >>=(unsigned int)", "?")
	print("\njust for fun")
	diagnose("int foo::bar(MyClass arg1)", "?")
	
