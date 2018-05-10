import os
import datetime
from flask import Flask, request, render_template
from resultsreader import ResultsReader
from properties import Properties
from examplequeries import ExampleResults

SCRAPY_EXEC = "scrapy"

def download_snippets(pp):
	"""
	Calls the DOWNLOADER component in order to download data based on the user's query.
	"""
	## If running on windows you may have to edit the file:
	## \python-3.6.3.amd64\Lib\site-packages\twisted\internet\_win32stdio.py
	## and add the import pywintypes before the import win32api
	print("Downloading to file: " + pp.SRESULTS_A)
	if os.path.exists(pp.SRESULTS_A):
		os.remove(pp.SRESULTS_A)
	os.system(SCRAPY_EXEC + ' crawl googlesnippets -a query="' + pp.query + '" -s LOG_ENABLED=1' + ' -o ' + pp.SRESULTS_A)

def evaluate_apis(pp):
	"""
	Calls the API evaluator in MINER component.
	"""
	from MINER.API_MINER.api_evaluator import run_api_evaluator
	run_api_evaluator(pp)


def evaluate_readability(pp):
	"""
	Calls the readability evaluator in MINER component.
	"""
	from MINER.READABILITY_EVALUATOR.readability_evaluator import run_readability_evaluator
	run_readability_evaluator(pp)


def cluster_present_results(pp):
	"""
	Calls the CLUSTERER component.
	"""
	from CLUSTERER.kmeans_clustering import run_clustering
	run_clustering(pp)


def main(query, remaddress):
	current_date_time = remaddress.replace('.', '_') + "___" + datetime.datetime.now().isoformat('_').replace('-','_').replace(':','_').replace('.','_')
	pp = Properties(query, thepath = current_date_time)
	download_snippets(pp)
	evaluate_apis(pp)
	evaluate_readability(pp)
	cluster_present_results(pp)
	return current_date_time

if __name__ == "__main__":
	xr = ExampleResults(os.getcwd())
	rr = ResultsReader()
	class MyFlask(Flask):
		jinja_options = dict(Flask.jinja_options)
	app = MyFlask(__name__)
	@app.route("/")
	def index():
		return render_template('index.html', example_queries = xr.read_example_queries())
	@app.route("/results", methods=['POST'])
	def results():
		query = request.form['text']
		thepath = request.form['thepath'] if 'thepath' in request.form else None
		if query.startswith("___"):
			query = query[3:]
		else:
			if not xr.is_example_query(query):
				thepath = main(query, request.remote_addr)
		if xr.is_example_query(query):
			pp = Properties(query, xr.get_example_query_index(query))
		else:
			pp = Properties(query, thepath = thepath)
		finalresult = rr.read_file(pp.RESULTS_C, pp.RESULTS_D)
		return render_template('results.html', results = finalresult, query = query, example_queries = xr.read_example_queries(), thepath = thepath)
	@app.route("/cluster", methods=['POST'])
	def cluster():
		query = request.form['query']
		thepath = request.form['thepath'] if 'thepath' in request.form else None
		if xr.is_example_query(query):
			pp = Properties(query, xr.get_example_query_index(query))
		else:
			pp = Properties(query, thepath = thepath)
		finalresult = rr.read_file(pp.RESULTS_C, pp.RESULTS_D)
		selcluster = request.form['explore']
		cluster_num = int(selcluster.split()[-1]) - 1
		return render_template('cluster.html', cluster_num = cluster_num + 1, cluster = finalresult["clusters"][cluster_num], query = query, example_queries = xr.read_example_queries(), thepath = thepath)
	app.run('0.0.0.0', 6060, debug = False)
	
	
