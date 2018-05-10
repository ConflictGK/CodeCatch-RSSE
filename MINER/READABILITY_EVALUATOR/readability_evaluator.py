import json
import pandas as pd
import MINER.READABILITY_EVALUATOR.code_metrics as cm
from sklearn.preprocessing import normalize
from sklearn.externals import joblib
import sys
sys.path.append('../../')

CLF_FILENAME = 'AdaBoostClassifier.pkl' # or 'RandomForestClassifier.pkl' or 'KNNClassifier.pkl'
API_RATIO_THRESHOLD = 0.60

def run_readability_evaluator(pp):
	with open(pp.RESULTS_B, 'r') as datafile:
		query_data = json.load(datafile)

	clf = joblib.load('MINER/READABILITY_EVALUATOR/' + CLF_FILENAME)
	
	
	total = 0	   # total snippets tested for readability
	passed = 0	  # total snippets passed readability test
	
	for i, page_result in enumerate(query_data):
		sys.stdout.write("\rProcessing snippets of url {} / {}".format(
			i + 1, len(query_data)))
	
		for segment in page_result['segments']:
	
#			if segment['semicolon'] and segment['length']:
			metrics = {}
			snippet = segment['code']
			snippet = snippet.split('\n')

			metrics.update(cm.count_line_length(snippet))
			metrics.update(cm.count_identifiers(snippet))
			metrics.update(cm.count_identifier_length(snippet))
			metrics.update(cm.count_indentation(snippet))
			metrics.update(cm.count_keywords(snippet))
			metrics.update(cm.count_numbers(snippet))
			metrics.update(cm.count_comments(snippet))
			metrics.update(cm.count_periods(snippet))
			metrics.update(cm.count_commas(snippet))
			metrics.update(cm.count_spaces(snippet))
			metrics.update(cm.count_parenthesis(snippet))
			metrics.update(cm.count_arithmetic_operators(snippet))
			metrics.update(cm.count_comparison_operators(snippet))
			metrics.update(cm.count_assignments(snippet))
			metrics.update(cm.count_branches(snippet))
			metrics.update(cm.count_loops(snippet))
			metrics.update(cm.count_blank_lines(snippet))
			metrics.update(cm.count_max_char_ocurrences(snippet))
			metrics.update(cm.count_max_identifier_occurences(snippet))

			X_pred = pd.Series(metrics)
			# Reshape from (25, 1) vector to (1, 25)
			X_pred = X_pred.values.reshape(1, -1)
			# Normalize the code metrics vector
			X_pred = normalize(X_pred)

			# Predict readability for each snippet
			# False(0) --> Less Readable
			# True(1)  --> More Readable
			total += 1
			if clf.predict(X_pred):
				segment['readability'] = True
				passed += 1
			else:
				segment['readability'] = False
#			else:
#				segment['readability'] = None
	
		sys.stdout.flush()
	
	print("\nSnippets passed readability test = {} / {}".format(passed, total))
	# Update json file with readability metric
	with open(pp.RESULTS_C, 'w') as datafile:
		json.dump(query_data, datafile, indent=2)

if __name__ == "__main__":
	run_readability_evaluator()
