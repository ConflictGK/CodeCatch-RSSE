import os
import re
import json
import pyastyle
from pygments import highlight
from pygments.lexers import JavaLexer
from pygments.formatters import HtmlFormatter

p = re.compile('import (.*);')

class ResultsReader:

	def read_file(self, query_file, results_file):
		# Read data
		with open(results_file) as infile:
			finalresult = json.load(infile)
		with open(query_file) as infile:
			queryresults = {}
			for page in json.load(infile):
				queryresults[page["url"]] = {}
				for segment in page["segments"]:
					queryresults[page["url"]][segment["in_page_order"]] = segment
		
		for fcluster in finalresult["clusters"]:
			fcluster["Score"] = []
			fcluster["imports"] = {}
			top_apis = fcluster["top_apis_by_cluster"]
			new_top_apis = []
			for fsnippet in fcluster["cluster_snippets"]:
				# Get stats and method invocations
				snip = queryresults[fsnippet["Url"]][fsnippet["In_Page_Order"]]
				fsnippet["API_Ratio"] = snip["API_Ratio"]
				fsnippet["readability"] = snip["readability"] if snip["readability"] == True else False
				MethodInvocationsFull = fsnippet["MethodInvocations"]
				MethodInvocations = []
				for mi in MethodInvocationsFull:
					if mi.endswith('__init__'):
						MethodInvocations.append(mi.split('.')[0])
					else:
						if len(mi.split('.')) > 1:
							MethodInvocations.append(mi.split('.')[1])
				fsnippet["MethodInvocationsFull"] = MethodInvocationsFull
				fsnippet["MethodInvocations"] = MethodInvocations

				# Compute snippet API score
				for mi in MethodInvocationsFull:
					fsnippet["API_Score"] = snip["APIsProjects"][mi] / 1000 if mi in snip["APIsProjects"] else 0

				# Find API qualified names
				for api in top_apis:
					for m in MethodInvocationsFull:
						if api == m.lower() and m not in new_top_apis:
							new_top_apis.append(m)

				# Format code
				code = fsnippet["Code"]
				fsnippet["Code"] = ';\n'.join(code.split(';')) if '\n' not in code else code 
				fsnippet["formatted_code"] = pyastyle.format(fsnippet["Code"], "--style=java --delete-empty-lines")
				fsnippet["full_code"] = highlight(fsnippet["formatted_code"], JavaLexer(), HtmlFormatter())

				# Find imports
				fsnippet["imports"] = p.findall(fsnippet["formatted_code"])
				fsnippet["imports"] += ['.'.join(snip["APIsQualifiedNames"][m].split('.')[:-1]) for m in MethodInvocationsFull if m in snip["APIsQualifiedNames"]]
				for im in fsnippet["imports"]:
					if len(im) <= 100:# and not im.endswith("Exception"):
						fcluster["imports"][im] = 1 if im not in fcluster["imports"] else fcluster["imports"][im] + 1

				# Highlight api calls
				lines = fsnippet["full_code"].split('\n')
				hapicalls = 0
				for mi in MethodInvocations:
					for l, line in enumerate(lines):
						if 'import' not in line:
							while '<span class="na">' + mi + '</span>' in line:
								line = line.replace('<span class="na">' + mi + '</span>', '<span class="na nana">' + mi + '</span>')
								hapicalls += 1
						while '<span class="n">' + mi + '</span>' in line:
							line = line.replace('<span class="n">' + mi + '</span>', '<span class="n nana">' + mi + '</span>')
						lines[l] = line
				fsnippet["Num_Highlighted_API_Calls"] = hapicalls
				fsnippet["full_code"] = '\n'.join(lines)
				fcluster["Score"].append(fsnippet["Score"])

				# Get important lines
				first = fsnippet["full_code"][0:28]
				lines = fsnippet["full_code"][28:-14].split('\n')
				last = fsnippet["full_code"][-13:]
				newlineids = []
				for l, line in enumerate(lines):
					if any('<span class="na nana">' + mi + '</span>' in line for mi in MethodInvocations):
						newlineids.append(l)
					if any('<span class="n nana">' + mi + '</span>' in line for mi in MethodInvocations):
						newlineids.append(l)
				newlines = []
				used_ids = set()
				for newlineid in newlineids:
					for k in [-1, 0, 1]:
						if newlineid + k >= 0 and newlineid + k < len(lines) and newlineid + k not in used_ids:
							newlines.append(lines[newlineid + k])
							used_ids.add(newlineid + k)
				fsnippet["invocations_code"] = first + '\n'.join(newlines) + last
				fsnippet["LOC"] = len([line for line in lines if line.strip()])
			# Create score
			scores = fcluster["Score"]
			fcluster["Score"] = sum(scores[:min(10, len(scores))]) / len(scores[:min(10, len(scores))])
			
			if len(fcluster["imports"]) < 5:
				for j, _ in enumerate(fcluster["cluster_snippets"]):
					if "API_Qualified_Names" in fsnippet:
						fsnippet["API_Qualified_Names"] = [im.split('.')[-1] for im in fsnippet["API_Qualified_Names"]]
						for im in fsnippet["API_Qualified_Names"]:
							if im not in fcluster["imports"]:
								if len(im) <= 100:
									fcluster["imports"][im] = 1

			fcluster["top_apis_by_cluster"] = new_top_apis

			fcluster["API_Score"] = sum([fsnippet["API_Score"] for fsnippet in fcluster["cluster_snippets"]]) / len(fcluster["cluster_snippets"])
			fcluster["cluster_snippets"].sort(reverse = True, key = lambda x: (x["API_Score"], x["Score"]))
		finalresult["clusters"].sort(reverse = True, key = lambda x: x["API_Score"])
		return finalresult
