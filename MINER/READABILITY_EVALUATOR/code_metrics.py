'''
Description:
This module calculates all the code metrics described by Buse et al.

Function-list:
-count_line_length:                 avg/max line length(# characters)
-count_identifiers:                 avg/max # identifiers
-count_identifier_length            avg/max identifier length
-count_indentation:                 avg/max indentation (preceding whitespace)
-count_keywords:                    avg/max # keywords
-count_numbers:                     avg/max # numbers
-count_comments:                    avg     # comments
-count_periods:                     avg     # periods
-count_commas:                      avg     # commas
-count_spaces:                      avg     # spaces
-count_parenthesis:                 avg     # parenthesis
-count_arithmetic_operators:        avg     # arithmetic operators
-count_comparison_operators:        avg     # comparison operators
-count_assignments:                 avg     # assignments (=)
-count_branches:                    avg     # branches (if/switch)
-count_loops:                       avg     # loops (for/while)
-count_blank_lines:                 avg     # blank lines
-count_max_char_ocurrences:         max     # occurences of any single character
-count_max_identifier_occurences:   max     # occurences of any single identifier

For more info read:
Learning a Metric for Code Readability
Raymond P.L. Buse, Westley Weimer
'''
import numpy as np
import javalang
from javalang import tokenizer
from collections import Counter
from itertools import chain

# token type constants
JAVA_IDENTIFIER = javalang.tokenizer.Identifier
JAVA_KEYWORD = javalang.tokenizer.Keyword
JAVA_NUMBER = [javalang.tokenizer.BinaryInteger,
               javalang.tokenizer.DecimalFloatingPoint,
               javalang.tokenizer.DecimalInteger, javalang.tokenizer.FloatingPoint,
               javalang.tokenizer.HexFloatingPoint, javalang.tokenizer.HexInteger,
               javalang.tokenizer.Integer, javalang.tokenizer.OctalInteger]

JAVA_ARITHMETIC_OPERATORS = '+-*/%'
JAVA_COMPARISON_OPERATORS = ['==', '!=', '>', '>=', '<', '<=']
JAVA_COMMENTS = ["/*", "//"]

def count_line_length(snippet):
	'''
	Calculates the average and maximun line length of the given snippet.
	'''
	line_length = []
	for line in snippet:
		words = line.split()
		line_length.append(sum(len(word) for word in words))
	
	if line_length:
		max_line_length = max(line_length)
		avg_line_length = np.mean(line_length)
	else:
		max_line_length = 0
		avg_line_length = 0

	return {
		'max_line_length': max_line_length,
		'avg_line_length': avg_line_length
	}

def count_identifiers(snippet):
	'''
	Calculates the average per line and maximum in any line identifiers in snippet.
	'''
	perline_identifiers = []
	for line in snippet:
		try:
			line_tokens = list(tokenizer.tokenize(line))
			perline_identifiers.append([token.value for token in line_tokens
										if type(token) == JAVA_IDENTIFIER])
		except Exception as err:
			perline_identifiers = []
			break
	# maximum number of identifiers in any line
	if perline_identifiers:
		max_identifiers_perline = len(max(perline_identifiers, key=len))
		total_identifiers = sum([len(l) for l in perline_identifiers])
		avg_identifiers_perline = total_identifiers / len(perline_identifiers)
	else:
		max_identifiers_perline = 0
		avg_identifiers_perline = 0

	return {
		'max_identifiers_perline': max_identifiers_perline,
		'avg_identifiers_perline': avg_identifiers_perline,
	}

def count_identifier_length(snippet):
	'''
	Calculates the average and maximum identifier length in snippet.
	'''
	perline_identifiers = []
	total_lines = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			perline_identifiers.append([token.value for token in line_tokens
										if type(token) == JAVA_IDENTIFIER])
		except Exception as err:
			perline_identifiers = []
			break

	# concatenate sublists of identifiers into one list.
	total_identifiers = list(chain.from_iterable(perline_identifiers))
	if total_identifiers:
		max_identifier_length = len(max(total_identifiers, key=len))
		avg_identifier_length = sum(map(len, total_identifiers)) / len(total_identifiers)
	else:
		max_identifier_length = 0
		avg_identifier_length = 0

	return {
		'max_identifier_length': max_identifier_length,
		'avg_identifier_length': avg_identifier_length
	}

def count_indentation(snippet, tabsize=4):
	'''
	Calculates the average per line and maximum in any line indentation in snippet.
	'''
	indentation = []
	for line in snippet:
		expanded_line = line.expandtabs(tabsize)
		indentation.extend([0 if expanded_line.isspace()
							else len(expanded_line) - len(expanded_line.lstrip())])

	if indentation:
		# max indentation in snippet
		max_indentation = max(indentation)

		# average indentation in snippet
		avg_indentation = sum(indentation) / len(indentation)
	else:
		max_indentation = 0
		avg_indentation = 0

	return {
		'max_indentation': max_indentation,
		'avg_indentation': avg_indentation
	}

def count_keywords(snippet):
	'''
	Calculates the average per line and maximum in any line keywords in snippet.
	'''
	perline_keywords = []
	for line in snippet:
		try:
			line_tokens = list(tokenizer.tokenize(line))
			perline_keywords.append([token.value for token in line_tokens
									 if type(token) == JAVA_KEYWORD])
		except Exception as err:
			perline_keywords = []
			break

	if perline_keywords:		
		# maximum number of keywords in any line
		max_keywords_perline = len(max(perline_keywords, key=len))

		# total keywords in snippet
		total_keywords = sum([len(l) for l in perline_keywords])

		# average keywords per line in snippet
		avg_keywords_perline = total_keywords / len(perline_keywords)
	else:
		max_keywords_perline = 0
		avg_keywords_perline = 0

	return {
		'max_keywords_perline': max_keywords_perline,
		'avg_keywords_perline': avg_keywords_perline
	}

def count_numbers(snippet):
	'''
	Calculates the average per line and maximum in any line numbers in snippet.
	'''
	perline_numbers = []
	for line in snippet:
		try:
			line_tokens = list(tokenizer.tokenize(line))
			perline_numbers.append([token.value for token in line_tokens
									if type(token) in JAVA_NUMBER])
		except Exception as err:
			perline_numbers = []
			break

	if perline_numbers:
		# maximum number of number variables in any line
		max_numbers_perline = len(max(perline_numbers, key=len))

		# total number variables in snippet
		total_numbers = sum([len(l) for l in perline_numbers])

		# average numbers per line in snippet
		avg_numbers_perline = total_numbers / len(perline_numbers)
	else:
		max_numbers_perline = 0
		avg_numbers_perline = 0

	return {
		'max_numbers_perline': max_numbers_perline,
		'avg_numbers_perline': avg_numbers_perline
	}

def count_comments(snippet):
	'''
	Calculates the average per line comments in snippet
	'''
	total_lines = 0
	total_comments = 0
	for line in snippet:
		total_lines += 1
		if any(comment in line for comment in JAVA_COMMENTS):
			total_comments += 1

	if total_lines > 0:
		avg_comments_perline = total_comments / total_lines
	else:
		avg_comments_perline = 0

	return {
		'avg_comments_perline': avg_comments_perline
	}


def count_periods(snippet):
	'''
	Calculates the average per line periods (.) in snippet.
	'''
	total_lines = 0
	total_periods = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_periods += sum([1 for token in line_tokens if token.value == "."])
		except Exception as err:
			total_periods = 0
			break

	if total_lines > 0:
		avg_periods_perline = total_periods / total_lines
	else:
		avg_periods_perline = 0

	return {
		'avg_periods_perline': avg_periods_perline
	}

def count_commas(snippet):
	'''
	Calculates the average per line periods (,) in snippet.
	'''
	total_lines = 0
	total_commas = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_commas += sum([1 for token in line_tokens if token.value == ","])
		except Exception as err:
			total_commas = 0
			break

	if total_lines > 0:
		avg_commas_perline = total_commas / total_lines
	else:
		avg_commas_perline = 0

	return {
		'avg_commas_perline': avg_commas_perline
	}

def count_spaces(snippet):
	'''
	Calculates the average per line white spaces in snippet
	'''
	total_spaces = 0
	total_lines = 0
	for line in snippet:
		total_lines += 1
		line = line.strip() # clear spaces from left and right in line
		total_spaces += line.count(" ")

	if total_lines > 0:
		avg_spaces_perline = total_spaces / total_lines
	else:
		avg_spaces_perline = 0

	return {
		'avg_spaces_perline': avg_spaces_perline
	}

def count_parenthesis(snippet):
	'''
	Calculates the average per line parenthesis ((, )) in snippet.
	'''
	total_parenthesis = 0
	total_lines = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_parenthesis += sum([1 for token in line_tokens
									  if token.value == "(" or token.value == ")"])
		except Exception as err:
			total_parenthesis = 0
			break

	if total_lines > 0:
		avg_parenthesis_perline = total_parenthesis / total_lines
	else:
		avg_parenthesis_perline = 0

	return {
		'avg_parenthesis_perline': avg_parenthesis_perline
	}

def count_arithmetic_operators(snippet):
	'''
	Calculates the average per line arithmetic operators in snippet.
	'''
	total_lines = 0
	total_operators = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_operators += sum([1 for token in line_tokens
									if token.value in JAVA_ARITHMETIC_OPERATORS])
		except Exception as err:
			total_operators = 0
			break

	if total_lines > 0:
		avg_arithmetic_operators_perline = total_operators / total_lines
	else:
		avg_arithmetic_operators_perline = 0

	return {
		'avg_arithmetic_operators_perline': avg_arithmetic_operators_perline
	}

def count_comparison_operators(snippet):
	'''
	Calculates the average per line comparison operators in snippet.
	'''
	total_lines = 0
	total_operators = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_operators += sum([1 for token in line_tokens
									if token.value in JAVA_COMPARISON_OPERATORS])
		except Exception as err:
			total_operators = 0
			break

	if total_lines > 0:
		avg_comparison_operators_perline = total_operators / total_lines
	else:
		avg_comparison_operators_perline = 0

	return {
		'avg_comparison_operators_perline': avg_comparison_operators_perline
	}

def count_assignments(snippet):
	'''
	Calculates the average per line assignments (=) in snippet.
	'''
	total_lines = 0
	total_assignments = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_assignments += sum([1 for token in line_tokens
									  if token.value == "="])
		except Exception as err:
			total_assignments = 0
			break

	if total_lines > 0:
		avg_assignments_perline = total_assignments / total_lines
	else:
		avg_assignments_perline = 0

	return {
		'avg_assignments_perline': avg_assignments_perline
	}

def count_branches(snippet):
	'''
	Calculates the average per line branches (if/switch) in snippet.
	'''
	total_branches = 0
	total_lines = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_branches += sum([1 for token in line_tokens
								   if token.value == "if" or token.value == "switch"])
		except Exception as err:
			total_branches = 0
			break

	if total_lines > 0:
		avg_branches_perline = total_branches / total_lines
	else:
		avg_branches_perline = 0

	return {
		'avg_branches_perline': avg_branches_perline
	}

def count_loops(snippet):
	'''
	Calculates the average per line loops (for/while) in snippet.
	'''
	total_loops = 0
	total_lines = 0
	for line in snippet:
		total_lines += 1
		try:
			line_tokens = list(tokenizer.tokenize(line))
			total_loops += sum([1 for token in line_tokens
								if token.value == "for" or token.value == "while"])
		except Exception as err:
			total_loops = 0
			break

	if total_lines > 0:
		avg_loops_perline = total_loops / total_lines
	else:
		avg_loops_perline = 0

	return {
		'avg_loops_perline': avg_loops_perline
	}

def count_blank_lines(snippet):
	'''
	Calculates the average blank lines in snippet.
	'''
	total_lines = 0
	total_blank_lines = 0
	for line in snippet:
		total_lines += 1
		if line.isspace():
			total_blank_lines += 1

	if total_lines > 0:
		avg_blank_lines = total_blank_lines / total_lines
	else:
		avg_blank_lines = 0

	return {
		'avg_blank_lines': avg_blank_lines
	}

def count_max_char_ocurrences(snippet):
	'''
	Calculates the maximum occurences of any character in any line in snippet.
	'''
	top_freq_perline = [] # list with highest char frequency in each line

	for line in snippet:
		line = line.replace(" ", "") # strip line from whitespace
		line_char_freq = Counter(line)
		if line_char_freq: # avoid empty lines
			line_top_char_freq = line_char_freq.most_common(1)[0][1]
			top_freq_perline.append(line_top_char_freq)

	if top_freq_perline:
		max_char_occurences = max(top_freq_perline)
	else:
		max_char_occurences = 0

	return {
		'max_char_ocurrences': max_char_occurences
	}

def count_max_identifier_occurences(snippet):
	'''
	Calculates the maximum occurences of any identifier in any line in snippet.
	'''
	top_freq_perline = [] # list with highest identifier frequency in each line

	for line in snippet:
		try:
			line_tokens = list(tokenizer.tokenize(line))
			line_identifiers = [token.value for token in line_tokens
								if type(token) == JAVA_IDENTIFIER]
			identifier_freq = Counter(line_identifiers)
			if identifier_freq: # avoid lines without any identifiers
				top_identifier_freq = identifier_freq.most_common(1)[0][1]
			else:
				top_identifier_freq = 0
			top_freq_perline.append(top_identifier_freq)
		except Exception as err:
			top_freq_perline = []
			break

	if top_freq_perline:
		max_identifier_freq = max(top_freq_perline)
	else:
		max_identifier_freq = 0

	return {
		'max_identifier_occurences': max_identifier_freq
	}
