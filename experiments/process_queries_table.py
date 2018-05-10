import json

queries = []
with open("queries.txt") as infile:
	for line in infile:
		line = line.strip()
		if line:
			queries.append(line)

header = ["ID", "Query", "Clusters", "Snippets"]#, "Snippets/Cluster"]
stats = []
for query_id in range(len(queries)):
	with open("query" + str(query_id) + "/resultsD.json") as infile:
		data = json.load(infile)
		clusters = len(data["clusters"])
		snippets = sum([len(cluster["cluster_snippets"]) for cluster in data["clusters"]])
		stats.append([query_id + 1, queries[query_id], clusters, snippets])#, snippets / clusters])

print('\\begin{tabular}{clccc}')
print('\\toprule')
print(' & '.join(header) + ' \\\\')
print('\\midrule')
for s in stats:
	print(' & '.join(str(i) for i in s) + ' \\\\')
print('\\bottomrule')
print('\\end{tabular}')

