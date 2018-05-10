import os
import datetime
from shutil import copyfile
from codecatch import download_snippets, evaluate_apis, evaluate_readability, cluster_present_results
from properties import Properties

EXPERIMENTS_DIR = os.getcwd() + os.path.sep + "experiments" + os.path.sep

queries = []
with open(EXPERIMENTS_DIR + "queries.txt") as infile:
	for line in infile:
		line = line.strip()
		if line:
			queries.append(line)
if not os.path.exists(EXPERIMENTS_DIR):
	os.makedirs(EXPERIMENTS_DIR)
for i, query in enumerate(queries):
	if not os.path.exists(EXPERIMENTS_DIR + "query" + str(i) + "/"):
		print("\n\nQUERY " + str(i) + ": " + query)
		current_date_time = datetime.datetime.now().isoformat('_').replace('-','_').replace(':','_').replace('.','_')
		pp = Properties(query, thepath = current_date_time)
		download_snippets(pp)
		evaluate_apis(pp)
		evaluate_readability(pp)
		cluster_present_results(pp)
		os.makedirs(EXPERIMENTS_DIR + "query" + str(i) + "/")
		EXPERIMENTS_QUERY_DIR = EXPERIMENTS_DIR + "query" + str(i) + "/"
		EXPERIMENTS_RESULTS_A = EXPERIMENTS_QUERY_DIR + 'resultsA.json'
		EXPERIMENTS_RESULTS_B = EXPERIMENTS_QUERY_DIR + 'resultsB.json'
		EXPERIMENTS_RESULTS_C = EXPERIMENTS_QUERY_DIR + 'resultsC.json'
		EXPERIMENTS_RESULTS_D = EXPERIMENTS_QUERY_DIR + 'resultsD.json'
		EXPERIMENTS_RESULTS_S = EXPERIMENTS_QUERY_DIR + 'resultsS.json'
		copyfile(pp.RESULTS_A, EXPERIMENTS_RESULTS_A)
		copyfile(pp.RESULTS_B, EXPERIMENTS_RESULTS_B)
		copyfile(pp.RESULTS_C, EXPERIMENTS_RESULTS_C)
		copyfile(pp.RESULTS_D, EXPERIMENTS_RESULTS_D)
		copyfile(pp.RESULTS_S, EXPERIMENTS_RESULTS_S)
	
