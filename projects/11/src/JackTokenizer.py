'''
Tom Granot-Scalosub - 308020734
Daniel Bachar - 201242120
Compiler - Jack Tokenizer
'''
# Used for tokenizing code. Make sure to do `pip install nltk` before going forward.
import nltk
from nltk import word_tokenize
from nltk.tokenize import WhitespaceTokenizer

# After you've downloaded the `punkt` package once, you can comment out the line below.
# This will speed up tokenization.
nltk.download('punkt')

# Regex for fun and profit!
import re

# Handle keywords
keyWords = ['class','constructor','function','method','field','static', 'var','int','char',
'boolean','void','true','false','null','this', 'let','do','if','else','while','return']


def isKeyWord(string):
	return string in keyWords

def keyWord(string):
	return string.upper()

# Handle symbols
symbols = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']
parsed_symbols = ["&lt;","&gt;","&quot;","&amp;"]

def isSymbol(string):
	return (string in symbols) or (string in parsed_symbols)

def symbol(string):
	return string

# Handle string constants
def isStringConstant(string):
	#forbidden_chars = ['\'','\"',"\n"]
	#return (not(any([(fc in string) for fc in forbidden_chars])) & string.startswith("$$$"))
	return string.startswith("$$$")

def stringVal(string):
	return string.translate(None,'\"')

# Handle integer constants
def isIntegerConstant(string):
	try:
		num = int(string)
		return  0 <= num <= 32767
	except:
		return False

def intVal(string):
	return int(string)

# Handle identifiers
def isIdentifier(string):
	# Check for strings that DO NOT start with a digit and have only digits/letters/underscores in them
	p = re.compile("^[^0-9]?(?:[a-zA-Z_]+)$")
	return p.match(string)

def identifier(string):
	return string

# Decide on the type of a token
def tokenType(token):
	if isKeyWord(token):
		return "keyword"
	elif isSymbol(token):
		return "symbol"
	elif isStringConstant(token):
		return "stringConstant"
	elif isIdentifier(token):
		return "identifier"
	elif isIntegerConstant(token):
		return "integerConstant"
	else:
		return "ERROR IN DETERMINING TOKEN TYPE"
