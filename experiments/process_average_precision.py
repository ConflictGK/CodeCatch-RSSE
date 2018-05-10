import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 0.3

FIG_DIR = "C:/Users/themis/Desktop/RAISE2018/images/" if os.path.exists("C:/Users/themis/Desktop/RAISE2018/images/") else "C:/Users/user/Desktop/RAISE2018/images/"

def average_precision(examined_results, position=None):
	the_max_range = min(position, len(examined_results)) if position else examined_results
	correct_results = 0
	precision = []
	for i in range(the_max_range):
		if examined_results[i] == 1:
			correct_results += 1
			precision.append(float(correct_results) / float(i + 1))
		else:
			pass  # precision.append(0.0) see https://makarandtapaswi.wordpress.com/2012/07/02/intuition-behind-average-precision-and-map/
	return np.mean(precision)

queries = []
with open("queries.txt") as infile:
	for line in infile:
		line = line.strip()
		if line:
			queries.append(line)

with open("alldata.json") as infile:
	alldata = json.load(infile)

codecatch_avp = []
google_avp = []
results_to_keep = 15
for query in ["query" + str(query_id) for query_id in range(len(queries))]:
	codecatch_snippets = alldata["codecatch"][query][:results_to_keep]
	google_snippets = alldata["google"][query][:results_to_keep]
	codecatch_avp.append(average_precision(codecatch_snippets, 10))
	google_avp.append(average_precision(google_snippets, 10))

print("CodeCatch Mean Average Precision: " + str(sum(codecatch_avp) / len(codecatch_avp)))
print("Google Mean Average Precision: " + str(sum(google_avp) / len(google_avp)))

ind = np.arange(len(queries))
width = 0.35

fig, ax = plt.subplots()
fig.set_size_inches(4.5, 3.0)
rects1 = ax.bar(ind, codecatch_avp, width, color='r', hatch = '/')
rects2 = ax.bar(ind + width, google_avp, width, color='y', hatch = '\\')

ax.set_ylim([0.0, 1.14])
ax.set_ylabel('Average Precision')
ax.set_xlabel('Query ID')
ax.set_xticks(ind + width / 2)
ax.set_xticklabels([str(query_id + 1) for query_id in range(len(queries))])

ax.legend((rects1[0], rects2[0]), ('CodeCatch', 'Google'), handletextpad=0.4)

fig.tight_layout()

#fig.subplots_adjust(left=0.1, right=0.9)

plt.savefig(FIG_DIR + "averageprecision.eps")
plt.savefig(FIG_DIR + "averageprecision.pdf")

plt.show()

