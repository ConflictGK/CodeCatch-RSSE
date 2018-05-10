import os
import json

queries = []
with open("queries.txt") as infile:
	for line in infile:
		line = line.strip()
		if line:
			queries.append(line)

relevant = {}
if os.path.exists("relevant.json"):
	with open("relevant.json") as infile:
		relevant = json.load(infile)
for query_id in range(15):
	if "query" + str(query_id) not in relevant:
		relevant["query" + str(query_id)] = {}
	print("The query is " + queries[query_id])
	with open("query" + str(query_id) + "/resultsD.json") as infile:
		data = json.load(infile)
		for i, cluster in enumerate(data["clusters"]):
			for j, snippet in enumerate(cluster["cluster_snippets"]):
				snippet["In_Page_Order"] = str(snippet["In_Page_Order"])
				print("Annotating snippet " + snippet["In_Page_Order"] + " of page " + snippet["Url"])
				if snippet["Url"] not in relevant["query" + str(query_id)]:
					relevant["query" + str(query_id)][snippet["Url"]] = {}

				if snippet["In_Page_Order"] not in relevant["query" + str(query_id)][snippet["Url"]]:
					print('---------------------------------------------------------------------')
					relevant["query" + str(query_id)][snippet["Url"]][snippet["In_Page_Order"]] = 0
					print(snippet["Code"].encode('ascii', errors='ignore').decode('ascii'))
					print("Is this relevant? [y/n or s for stop]")
					choice = input().lower()
					while choice != "y" and choice != "n" and choice != "s":
						print("Please select a valid option [y/n or s for stop]")
						choice = input().lower()
					if choice == "y":
						relevant["query" + str(query_id)][snippet["Url"]][snippet["In_Page_Order"]] = 1
					elif choice == "n":
						relevant["query" + str(query_id)][snippet["Url"]][snippet["In_Page_Order"]] = 0
					elif choice == "s":
						del relevant["query" + str(query_id)][snippet["Url"]][snippet["In_Page_Order"]]
						with open("relevant.json", 'w') as outfile:
							json.dump(relevant, outfile, indent=3)
						exit()
