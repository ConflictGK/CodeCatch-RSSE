'''
Description:
This module calculates code metrics for Buse Snippets dataset (100 snippets)
and organized them in json file in nested dictionaries form.
To access the code metrics (e.g. for 1.jsnp):
Load data from json file and then:
data['1.jsnp'] --> will return a dictionary with 25 code metrics.
'''
import os
import sys
import logging
import json
from collections import defaultdict
import code_metrics as cm

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def gather_code_metrics(snippet):
	'''
	Gathers all code metrics for the given as input snippet and organizes them
	in a dictionary form.
	'''
	code_metrics = {}

	code_metrics.update(cm.count_line_length(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_identifiers(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_identifier_length(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_indentation(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_keywords(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_numbers(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_comments(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_periods(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_commas(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_spaces(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_parenthesis(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_arithmetic_operators(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_comparison_operators(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_assignments(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_branches(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_loops(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_blank_lines(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_max_char_ocurrences(snippet))
	snippet.seek(0)
	code_metrics.update(cm.count_max_identifier_occurences(snippet))

	return code_metrics



if __name__ == "__main__":
	path = os.path.join(os.getcwd(), "Buse_Snippets")
	file_extension = ".jsnp"
	output_file = "buse_code_metrics.json"

	snippet_code_metrics = defaultdict(dict)

	for filename in os.listdir(path):
		if filename.endswith(file_extension):
			sys.stdout.write("\rProcessing snippet: {}...".format(filename))

			with open(os.path.join(path, filename), "r") as file:
				snippet_index = int(filename.split(".")[0]) # filename form = "x.jsnp"
				snippet_code_metrics[snippet_index] = gather_code_metrics(snippet=file)

			sys.stdout.flush()

	sys.stdout.write('\n')
	
	# sort dictionary by key (ascending order snippets)
	

	# Export measured code metrics to json output file.
	with open(os.path.join(os.getcwd(), output_file), 'w') as outfile:
		json.dump(snippet_code_metrics, outfile)
