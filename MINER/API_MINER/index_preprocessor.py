import os
import re
import json
from sequenceextractor import SequenceExtractor
from properties import PARENT_DIR

# To run this script, the latest version of the sequence extractor is required
# found at https://github.com/thdiaman/SequenceExtractor
# Then create a director "results" in this folder and set a directory with multiple projects
PROJECTS_DIR = "C:/elasticsearch/data/code/"

p = re.compile('import (.*);')
p2 = re.compile('FC_.*\((.*)\)')

sequence_extractor = SequenceExtractor(PARENT_DIR + "SequenceExtractor-0.4.jar", keep_function_call_types = True, flatten_output = False, keep_branches = True)

for repo_user in os.listdir(PROJECTS_DIR):
	for repo_name in os.listdir(PROJECTS_DIR + repo_user):
		if not repo_name.endswith('.json'):
			repo = repo_user + '/' + repo_name
			repo_safe_name = repo_user + '___' + repo_name
			if not os.path.exists('results/' + repo_safe_name + '.json'):
				result = {"project": repo, "files": []}
				rootpath = PROJECTS_DIR + repo + "/"

				allfiles = []
				for root, subFolders, files in os.walk(rootpath):
					for afile in files:
						if afile.endswith('.java'):
							allfiles.append((afile, os.path.join(root, afile)))
				lenallfiles = len(allfiles)
				i = 0
				import sys
				sys.stdout.write("\n\nParsing repo " + repo + " (" + str(lenallfiles) + " files)\n")
				for afile, afile_full_path in allfiles:
					i += 1
					sys.stdout.write('\r')
					sys.stdout.write("Progress: (%d files) %d%%" % (i, 100 * i / lenallfiles))
					sys.stdout.flush()
					result["files"].append({"filepath": afile_full_path[len(rootpath):].replace('\\', '/'), "imports": [], "sequences": []})
					with open(afile_full_path) as infile:
						try:
							code = infile.read().encode('ascii', errors = 'ignore').decode('ascii', errors = 'ignore')
							result["files"][-1]["imports"] = list(p.findall(code))
							sequences = sequence_extractor.parse_snippet(code)
						except:
							print("Parser Error on file: " + afile_full_path)
							#exit()
							sequences = None
						if sequences:
							try:
								sequences = re.sub("(\s|\[)(\w|\(|\))", r'\1"\2', sequences)
								sequences = re.sub("(\w|\(|\))(,|\])", r'\1"\2', sequences)
								sequences = re.sub("(\[)(\])", r'\1""\2', sequences)
								sequences = re.sub(",( ,)*", r',', sequences)
								sequences = re.sub(", ]", r']', sequences)
								nsequences = eval(sequences)
							except:
								print("Error on file: " + afile_full_path)
								print(sequences)
								#exit()
								sequences = []
							sequences = nsequences
						else:
							sequences = []
						newsequences = []
						for sequence in sequences:
							newsequence = []
							for item in sequence:
								if item.startswith("CI_"):
									newsequence.append(item[3:] + '__init__')
								elif item.startswith("FC_"):
									inner = list(p2.findall(item))
									if inner:
										newsequence.append(inner[0])
							if newsequence:
								newsequences.append(newsequence)
						result["files"][-1]["sequences"] = newsequences

				with open('results/' + repo_safe_name + '.json', 'w') as outfile:
					json.dump(result, outfile, indent = 3)
