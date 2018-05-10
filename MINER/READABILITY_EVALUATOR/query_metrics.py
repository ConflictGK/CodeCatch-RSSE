import json
import os
import sys
from collections import defaultdict
from code_metrics_collector import gather_code_metrics
from properties import EXPORT_FOLDER

QUERY_RESULTS_FILE = 'rankertest.json'
FILE_EXTENSION = '.jsnp'
OUTPUT_METRICS_FILE = "query_code_metrics.json"

if __name__ == "__main__":
	with open(QUERY_RESULTS_FILE) as datafile:
		data = json.load(datafile)

	snippet_index = 0

	for website in data:
		for segment in website['segments']:
			snippet = segment['code']
			snippet_index += 1
			export_file_name = str(snippet_index) + FILE_EXTENSION
			with open(os.path.join(EXPORT_FOLDER, export_file_name), "w") as export_file:
				export_file.write(snippet)

	snippet_code_metrics = defaultdict(dict)

	for filename in os.listdir(EXPORT_FOLDER):
		if filename.endswith(FILE_EXTENSION):
			sys.stdout.write("\rProcessing snippet: {}...".format(filename))

			with open(os.path.join(EXPORT_FOLDER, filename), "r") as file:
				snippet_index = int(filename.split(".")[0]) # filename form = "x.jsnp"
				snippet_code_metrics[snippet_index] = gather_code_metrics(snippet=file)
			sys.stdout.flush()

	sys.stdout.write('\n')

	# Export measured code metrics to json output file.
	with open(os.path.join(os.getcwd(), OUTPUT_METRICS_FILE), "w") as outfile:
		json.dump(snippet_code_metrics, outfile)
