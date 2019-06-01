'''
Tom Granot-Scalosub - 308020734
Daniel Bachar - 201242120
Compiler - Jack aNALYZER
'''
import sys
import os
from JackTokenizer import *
from CompilationEngine import *
from Agent import *

first_arg = sys.argv[1]

# Make a list of all the files we need to compile
files = []
orig_file_name = ""
orig_directory = ""

# If it's a file just add it to the list
if os.path.isfile(first_arg) & first_arg.endswith(".jack"):
	orig_file_name = first_arg
	files.append(orig_file_name)

# If it's a directory, append all jack files in it to the list (including directory name)
elif os.path.isdir(first_arg):
	orig_directory = first_arg
	for file in os.listdir(first_arg):
		if file.endswith(".jack"):
			# This is a small hack to replace \\ with \
			files.append(os.path.join(orig_directory,file))

# Notify if it's not a jack file or not a valid file/directory
else:
	print("WRONG FILE/DIRECTORY - CAN'T CREATE FILES LIST. EITHER NOT A JACK FILE, FILE/DIRECTORY DO NOT EXITST, OR SOMETHING IS REALLY REALLY BAD WITH YOUR MACHINE")
	exit()

# Should be at least one file in the
if (len(files) < 1):
	print("FILES LIST POPULATED INCORRECTLY, EXITING")
	exit()

# Run through all the files
for filename in files:

	# Open Jack code file for reading
	raw_file = open(filename,'r')

	# Create raw first-pass
	base_filename = filename.split(".")[0]
	raw_firstpass_filename = base_filename + "_FirstPass.jack"
	raw_firstpass = open(raw_firstpass_filename, 'w+')

	tokens = []
	# First pass through the file - remove comments and blank lines, break up string constants
	for line in raw_file:

		# If it's a comment or empty, skip the line
		line = line.strip()
		translated_command = ""
		if (line.startswith("//")) or (line.startswith("/**")) or (line.startswith("/*")) or (line.startswith("*")) or (len(line.strip()) == 0) :
			continue

		# Get rid of inline comments
		if ("//" in line):
			line = line.split("//")[0]

		# For each string constant, remove the double quotes and give it its own line
		# Note the reluctant regex quantifer between the quote marks, this allows for more than one
		# string constants in a single line. In addition, I've added $$$ at the beginning
		# of each string constant - this for easier tokenization later (note that $ is not part
		# of Jack's grammar)
		line = re.sub(r'\"(.*?)\"',r'\n$$$\1$$$\n',line)


		# Write line to raw first-pass file
		raw_firstpass.write(line + "\n")

	# Close raw file handlers amd delete intermediary file
	raw_file.close()
	raw_firstpass.close()

	# Open file handlers for second-pass file
	raw_firstpass = open(raw_firstpass_filename, 'r')
	raw_secondpass_filename = base_filename + "_SecondPass.jack"
	raw_secondpass = open(raw_secondpass_filename, 'w+')

	# Second pass at file - break up string before and after a dot, replace spaces in string constants with underscores
	for line in raw_firstpass:

		# For each string constant, replace spaces with underscores.
		# This will later allow the tokenizer to treat these as one strings

		if line.startswith("$$$"):
			line = line.replace(" ", "_")

		# For each expression with an excepted symbol in it, that is NOT part of a string constant
		# i.e. YES on Keyboard.readInt and NO on "This is. Bad", give the dot it's own line.
		# This is specifically done AFTER splitting to string constants to avoid splitting inside constants
		else:
			for symbol in symbols:
				line = line.replace(symbol,"\n" + symbol + "\n")

		# Write line to raw second-pass file
		raw_secondpass.write(line + "\n")

	# Close raw file handlers and delete intermediary file
	raw_firstpass.close()
	raw_secondpass.close()
	os.remove(raw_firstpass_filename)

	# Open cleaned file for tokenizing
	base_file = open(raw_secondpass_filename,'r')

	# Tokenize clean, second pass file (in-memory), close file handler and delete intermediary file
	raw_tokens = WhitespaceTokenizer().tokenize(base_file.read())
	base_file.close()
	os.remove(raw_secondpass_filename)


	### @@ from here on, you need to replaece the output file
	## With parsing the token list, playting with it, and
	## then adding it to an object that iterated over the list.
	## It needs to have a sort of linked list structure - it needs to be able
	## to run back and forth on a list, to make sense of the tokens.

	tokens = []
	# Pretty-print each token to output file
	for token in raw_tokens:

		# Get type of token
		token_type = tokenType(token)

		# Weird NLTK behaviour fix - it spits out `` instead of "
		token = token.replace("``","\"")

		# If it's a string constant, we need to clean it up
		if(token_type == "stringConstant"):
			#token = token.replace("$$$","")
			token = token.replace("_", " ")

		# If it's a symbol, make sure to format it properly
		# if(token == "<"):
		# 	token = "&lt;"
		# if(token == ">"):
		# 	token = "&gt;"
		# if(token == "\""):
		# 	token = "&quot;"
		# if(token == "&"):
		# 	token = "&amp;"

		tokens.append(token)

	# Create an agent and initialize it with the token list and the current file name
	agent = Agent(tokens, base_filename)

	# Start the compilation with the given agent
	# compiler = CompliationEngine(agent)
	# compiler.compile()
	compiler = CompliationEngine(agent)
	compiler.compileClass()
