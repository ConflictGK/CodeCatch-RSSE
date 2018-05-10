import json

queries = []
with open("queries.txt") as infile:
	for line in infile:
		line = line.strip()
		if line:
			queries.append(line)

relevant = {}
with open("relevant.json") as infile:
	relevant = json.load(infile)

alldata = {}
alldata["codecatch"] = {}
alldata["google"] = {}
# Iterate for each query
for query_id in range(len(queries)):
	with open("query" + str(query_id) + "/resultsD.json") as infile:
		resultsD = json.load(infile)
	with open("query" + str(query_id) + "/resultsC.json") as infile:
		resultsC = {}
		for page in json.load(infile):
			resultsC[page["url"]] = {}
			for segment in page["segments"]:
				resultsC[page["url"]][segment["in_page_order"]] = segment
	with open("query" + str(query_id) + "/resultsB.json") as infile:
		resultsA = json.load(infile)
	# Keep the results from codecatch
	codecatch_results = []
	for i, cluster in enumerate(resultsD["clusters"]):
		codecatch_results.append({"score": 0, "snippets": []})
		for j, snippet in enumerate(cluster["cluster_snippets"]):
			snip = resultsC[snippet["Url"]][snippet["In_Page_Order"]]
			MethodInvocationsFull = snippet["MethodInvocations"]
			for mi in MethodInvocationsFull:
				snippet["API_Score"] = snip["APIsProjects"][mi] / 1000 if mi in snip["APIsProjects"] else 0
			codecatch_results[-1]["snippets"].append(snippet)
		codecatch_results[-1]["score"] = sum([fsnippet["API_Score"] for fsnippet in cluster["cluster_snippets"]]) / len(cluster["cluster_snippets"])
		codecatch_results[-1]["snippets"].sort(reverse = True, key = lambda x: (x["API_Score"], x["Score"]))
	codecatch_results.sort(reverse = True, key = lambda x: x["score"])

	# Search strategy for switching clusters
	codecatch_snippets_per_cluster = []
	for cluster in codecatch_results:
		codecatch_snippets_per_cluster.append([])
		for snippet in cluster["snippets"]:
			codecatch_snippets_per_cluster[-1].append(relevant["query" + str(query_id)][snippet["Url"]][str(snippet["In_Page_Order"])])
			# SELECT SEARCH STRATEGY
			# (leave as is for simple serial search strategy)

			# Uncomment to switch cluster if the irrelevant results are more than the relevant
			relevant_results = sum(codecatch_snippets_per_cluster[-1])
			irrelevant_results = len(codecatch_snippets_per_cluster[-1]) - sum(codecatch_snippets_per_cluster[-1])
			if irrelevant_results > relevant_results:
				break

			# Uncomment to switch cluster if two consecutive results are irrelevant
			#if len(codecatch_snippets_per_cluster[-1]) > 2:
			#	last_2_results = codecatch_snippets_per_cluster[-1][-2:]
			#	if sum(last_2_results) == 0:
			#		break

	codecatch_snippets = [snippet for cluster in codecatch_snippets_per_cluster for snippet in cluster]
	alldata["codecatch"]["query" + str(query_id)] = codecatch_snippets

	# Keep the results from google
	google_snippets_dict = {}
	for res in resultsA:
		for segment in res["segments"]:
			if res["url position"] not in google_snippets_dict:
				google_snippets_dict[res["url position"]] = {}
			if res["url"] in relevant["query" + str(query_id)] and str(segment["in_page_order"]) in relevant["query" + str(query_id)][res["url"]]:
				google_snippets_dict[res["url position"]][segment["in_page_order"]] = \
												relevant["query" + str(query_id)][res["url"]][str(segment["in_page_order"])]
			else:
				google_snippets_dict[res["url position"]][segment["in_page_order"]] = 0
	google_snippets = []
	for u in sorted(google_snippets_dict.keys()):
		for v in sorted(google_snippets_dict[u].keys()):
			google_snippets.append(google_snippets_dict[u][v])
	alldata["google"]["query" + str(query_id)] = google_snippets

with open("alldata.json", 'w') as outfile:
	outfile.write('{\n   "codecatch": {\n')
	for query in ["query" + str(query_id) for query_id in range(len(queries))]:
		outfile.write('      "' + query + '": ' + str(alldata["codecatch"][query]) + (',\n' if query != "query" + str(len(queries) - 1) else "\n"))
	outfile.write('   },\n')
	outfile.write('   "google": {\n')
	for query in ["query" + str(query_id) for query_id in range(len(queries))]:
		outfile.write('      "' + query + '": ' + str(alldata["google"][query]) + (',\n' if query != "query" + str(len(queries) - 1) else "\n"))
	outfile.write('   }\n')
	outfile.write('}')
