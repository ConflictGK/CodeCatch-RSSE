import json

# run this script after running the index_constructor.oy

with open('api_calls_index_full.json') as infile:
	api_calls_full = json.load(infile)

api_calls = {}
for api_call, api_call_data in api_calls_full.items():
	if api_call_data["occurences_in_projects"] > 4:
		api_calls[api_call] = api_call_data

with open('api_calls_index.json', 'w') as outfile:
	json.dump(api_calls, outfile, indent = 3)
