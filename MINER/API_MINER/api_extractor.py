import os
import re
import json
import sys
sys.path.append('../../')

from MINER.API_MINER.sequenceextractor import SequenceExtractor


# exclude some very common MethodInvocations since they are used very frequently and not
# providing any essential information
EXCLUDE_METHODS = ['println', 'printStackTrace']

sequence_extractor = SequenceExtractor(os.getcwd() + os.path.sep + "SequenceExtractor-0.4.jar", keep_function_call_types = True, flatten_output = False, keep_branches = True)

def extract_api_tokens_from_snippet(snippet):
	try:
		code = snippet
		sequences = sequence_extractor.parse_snippet(code)
		sequences = re.sub("(\s|\[)(\w|\(|\))", r'\1"\2', sequences)
		sequences = re.sub("(\w|\(|\))(,|\])", r'\1"\2', sequences)
		sequences = re.sub("(\[)(\])", r'\1""\2', sequences)
		sequences = re.sub(",( ,)*", r',', sequences)
		sequences = re.sub(", ]", r']', sequences)
		sequences = eval(sequences)
	except:
		sequences = []
	final_sequence = []
	for sequence in sequences:
		for item in sequence:
			if item.startswith("CI_"):
				final_sequence.append(item[3:] + '.__init__')
			elif item.startswith("FC_"):
				p2 = re.compile('FC_.*\((.*)\)')
				inner = list(p2.findall(item))
				if inner:
					final_sequence.append(inner[0])
	return final_sequence

if __name__ == "__main__":
	# Load query data
	with open(RESULTS_A, 'r') as datafile:
		query_data = json.load(datafile)

	methods_total = []	  # total method invocations in entire query data file
	for site in query_data:
		for segment in site['segments']:
			# split code snippet in lines to parse as separate expressions
			methods = extract_api_tokens_from_snippet(segment['code'])
			methods = [method for method in methods if method not in EXCLUDE_METHODS]
			segment['methods'] = methods
			methods_total.extend(methods)

	print("Unique APIs: {}".format(len(set(methods_total))))

	# update json file with the MethodInvocations
	with open(RESULTS_B, 'w') as datafile:
		json.dump(query_data, datafile, indent=2)
