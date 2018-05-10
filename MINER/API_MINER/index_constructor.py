import os
import sys
import json

# run this script after running the index_preprocessor.oy

num_projects = 1000
projects = []
with open('1000moststarredprojects.txt') as infile:
	for line in infile:
		projects.append(line.strip())

api_calls = {}
nn = 0
for tproject in projects:
	if os.path.exists('results/' + tproject + '.json'):
		nn += 1
		sys.stdout.write('\r')
		sys.stdout.write("Progress: (%d projects) %d%%" % (nn-1, 100 * (nn-1) / num_projects))
		sys.stdout.flush()
		if nn == num_projects + 1:
			break
		with open('results/' + tproject + '.json') as infile:
			project = json.load(infile)
		api_calls_occured_in_this_project = set()
		for afile in project['files']:
			imports = {animport.split('.')[-1]: animport for animport in afile['imports']}
			imports.pop("*", None)
			api_calls_occured_in_this_file = set()
			for sequence in afile['sequences']:
				for api_call in sequence:
					if api_call.endswith('__init__'): api_call = api_call[:-len('__init__')] + '.__init__'
					if api_call not in api_calls:
						api_calls[api_call] = {"occurences_in_projects": 0, "occurences_in_files": 0, "occurences_in_snippets": 0, "qualified_name": api_call}
					obj_of_api_call = api_call.split('.')[0] if len(api_call.split('.')) > 0 else api_call
					method_of_api_call = api_call.split('.')[1] if len(api_call.split('.')) > 1 else api_call
					if obj_of_api_call in imports:
						api_calls[api_call]["qualified_name"] = imports[obj_of_api_call] + '.' + method_of_api_call
					api_calls[api_call]["occurences_in_snippets"] += 1
					if api_call not in api_calls_occured_in_this_file:
						api_calls[api_call]["occurences_in_files"] += 1
					api_calls_occured_in_this_file.add(api_call)
					if api_call not in api_calls_occured_in_this_project:
						api_calls[api_call]["occurences_in_projects"] += 1
					api_calls_occured_in_this_project.add(api_call)
with open('api_calls_index_full.json', 'w') as outfile:
	json.dump(api_calls, outfile, indent = 3)

