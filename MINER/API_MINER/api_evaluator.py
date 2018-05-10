import json
import sys
sys.path.append('../../')
from MINER.API_MINER.api_extractor import extract_api_tokens_from_snippet

DICT_FILE_NAME = 'api_calls_index.json'

def run_api_evaluator(pp):
	with open('MINER/API_MINER/' + DICT_FILE_NAME) as infile:
		dictionary = json.load(infile)

	# Open query data file
	with open(pp.RESULTS_A) as datafile:
		data = json.load(datafile)

	websites_without_segments = []
	for j, website in enumerate(data):
		segments_without_api_tokens = []
		for i, segment in enumerate(website['segments']):
			api_tokens = extract_api_tokens_from_snippet(segment['code'])
			if api_tokens:
				api_existance_status = dict()
				api_projects = dict()
				api_files = dict()
				api_snippets = dict()
				api_qualified_names = dict()
				for token in api_tokens:
					if token in dictionary:
						api_existance_status[token] = True
						api_projects[token] = dictionary[token]["occurences_in_projects"]
						api_files[token] = dictionary[token]["occurences_in_files"]
						api_snippets[token] = dictionary[token]["occurences_in_snippets"]
						if "qualified_name" in dictionary[token] and dictionary[token]["qualified_name"] != token:
							api_qualified_names[token] = dictionary[token]["qualified_name"]
					else:
						api_existance_status[token] = False
				segment['APIs'] = api_existance_status
				segment['APIsProjects'] = api_projects
				segment['APIsFiles'] = api_files
				segment['APIsSnippets'] = api_snippets
				segment['APIsQualifiedNames'] = api_qualified_names
				try:
					segment['API_Ratio'] = sum(1 for v in api_existance_status.values() if v) \
											/ len(api_existance_status)
				except ZeroDivisionError:
					segment['API_Ratio'] = 0
			else:
				segments_without_api_tokens.append(i)
		for i in sorted(segments_without_api_tokens, reverse=True):
			del website['segments'][i]
		if not website['segments']:
			websites_without_segments.append(j)
	for j in sorted(websites_without_segments, reverse=True):
		del data[j]

	with open(pp.RESULTS_B, 'w') as datafile:
		json.dump(data, datafile, indent=2)

if __name__ == '__main__':
	run_api_evaluator()
