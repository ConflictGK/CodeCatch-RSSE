import os
import json
import math
import numpy as np
import matplotlib.pyplot as plt

def reciprocal_rank(examined_results, cluster_id, max_number=200):
	for i, res in enumerate(examined_results):
		if res == cluster_id:
			return 1 / (i + 1)
	return 1 / max_number

def search_length(examined_results, cluster_id, max_number=200):
	number_of_irrelevant_results = 0
	for res in examined_results:
		if res == cluster_id:
			return number_of_irrelevant_results
		else:
			number_of_irrelevant_results += 1
	return max_number

def average_precision(examined_results, cluster_id, position=200):
	the_max_range = min(position, len(examined_results)) if position else examined_results
	correct_results = 0
	precision = []
	for i in range(the_max_range):
		if examined_results[i] == cluster_id:
			correct_results += 1
			precision.append(float(correct_results) / float(i + 1))
		else:
			pass  # precision.append(0.0) see https://makarandtapaswi.wordpress.com/2012/07/02/intuition-behind-average-precision-and-map/
	return np.mean(precision)

def discounted_cumulative_gain(examined_results, cluster_id, normalized = True, max_number=200):
	dcg = 0
	for i, res in enumerate(examined_results):
		if res == cluster_id:
			dcg += 1 / math.log(i + 1 + 1, 2)
	if normalized:
		ideal_examined_results = sorted(examined_results, reverse = True, key = lambda res: res == cluster_id)
		idcg = discounted_cumulative_gain(ideal_examined_results, cluster_id, normalized = False)
		return dcg / idcg if idcg > 0 else 0
	else:
		return dcg

FIG_DIR = "C:/Users/themis/Desktop/RAISE2018/images/" if os.path.exists("C:/Users/themis/Desktop/RAISE2018/images/") else "C:/Users/user/Desktop/RAISE2018/images/"
#METRIC = [search_length, "Search Length", "searchlength"]
METRIC = [reciprocal_rank, "Reciprocal Rank", "reciprocalrank"]
#METRIC = [average_precision, "Average Precision", "averageprecision"]
#METRIC = [discounted_cumulative_gain, "Discounted Cumulative Gain", "discountedcumulativegain"]

def metric(examined_results, cluster_id):
	return METRIC[0](examined_results, cluster_id)

queries = []
with open("queries.txt") as infile:
	for line in infile:
		line = line.strip()
		if line:
			queries.append(line)

with open("alldata_impls.json") as infile:
	alldata = json.load(infile)

codecatch_sl = {}
google_sl = {}

ind = list(range(1, 16))
results_to_keep = 100
for query in ["query" + str(query_id) for query_id in range(len(queries))]:
	clusters_range = range(len(alldata["codecatch"][query]))#range(0, 3)
	codecatch_sl[query] = []
	google_sl[query] = []
	for cluster in ["cluster" + str(cluster_id + 1) for cluster_id in clusters_range]:
		codecatch_snippets = alldata["codecatch"][query][cluster][:results_to_keep]
		google_snippets = alldata["google"][query][:results_to_keep]
		codecatch_sl[query].append(metric(codecatch_snippets, int(cluster[7:])))
		google_sl[query].append(metric(google_snippets, int(cluster[7:])))

# for query in ["query" + str(query_id) for query_id in range(len(queries))]:
# 	print(query[:5] + str(int(query[5]) + 1))
# 	clusters_range = range(len(alldata["codecatch"][query]))[:3]#range(0, 3)
# 	for cluster_id in clusters_range:
# 		print("   cluster %d:" %(cluster_id + 1), end =' ')
# 		print("CodeCatch: %.3f" %(codecatch_sl[query][cluster_id]), end =' ')
# 		print("Google: %.3f" %(google_sl[query][cluster_id]))

codecatch_values = np.asarray([codecatch_sl[query][cluster_id] for query in ["query" + str(query_id) for query_id in range(len(queries))] \
													for cluster_id in range(len(alldata["codecatch"][query]))[:3]])
google_values = np.asarray([google_sl[query][cluster_id] for query in ["query" + str(query_id) for query_id in range(len(queries))] \
													for cluster_id in range(len(alldata["codecatch"][query]))[:3]])

print("\nValues:")
print("CodeCatch: [" + ', '.join("%.3f" %d for d in codecatch_values) + "]")
print("Google: [" + ', '.join("%.3f" %d for d in google_values) + "]")
mrr_codecatch = np.mean(codecatch_values)
mrr_google = np.mean(google_values)
print("\nMeans:")
print("CodeCatch: %.3f" %(mrr_codecatch))
print("Google: %.3f" %(mrr_google))

print("\nPaired t-Test")
mrr_diff = (codecatch_values - google_values).astype(np.float64)
print("Differences: [" + ', '.join("%.3f" %d for d in mrr_diff) + "]")
mrr_diff_mean = np.mean(mrr_diff)
print("Mean Difference: %.3f" %mrr_diff_mean)
mrr_diff_var = np.var(mrr_diff, ddof = 1)
print("Variance of Difference: %.3f" %mrr_diff_var)
mrr_diff_standard_error_of_mean = np.sqrt(mrr_diff_var / float(len(mrr_diff)))
print("Standard Error of Mean Difference: %.3f" %mrr_diff_standard_error_of_mean)
t = np.divide(mrr_diff_mean,  mrr_diff_standard_error_of_mean)
print("t: %.3f" %t)

from scipy.stats.stats import _ttest_finish
t, p = _ttest_finish(float(len(mrr_diff) - 1), t)
print("p: %.15f" %p)

#from scipy.stats import ttest_rel as ttest
#print(ttest(codecatch_values, google_values))

width = 0.35

fig, ax = plt.subplots()
fig.set_size_inches(9.0, 2.65)##2.45)
rects1 = []
rects2 = []
ii = 0
positions = []
for query in ["query" + str(query_id) for query_id in range(len(queries))]:
	clusters_range = range(len(alldata["codecatch"][query]))[:3]#range(0, 3)
	ii += 1
	for cluster_id in clusters_range:
		ii += 2.5 * width
		if cluster_id == 1:
			positions.append(ii + width / 2 - 2.5 * width)
			positions.append(ii + width / 2)
			positions.append(ii + width / 2)
			positions.append(ii + width / 2 + 2.5 * width)
		rects1.append(ax.bar(ii, codecatch_sl[query][cluster_id], width, color='r', hatch = '/'))
		rects2.append(ax.bar(ii + width, google_sl[query][cluster_id], width, color='y', hatch = '\\'))

#ax.set_ylim([0.0, 1.14])
ax.set_ylabel(METRIC[1])
#ax.set_xlabel('Queries')
ax.set_xticks(positions)
ticklabels = []
for query_id in range(len(queries)):
	ticklabels.extend(["I1", "I2"] + ["\nQuery " + str(query_id + 1)] + ["I3"]) 
ax.set_xticklabels(ticklabels)
#ax.set_xticklabels(["Query " + str(query_id + 1) for query_id in range(len(queries))])

ax.set_xlim([0.5, 37.9])

#ax.legend((rects1[0], rects2[0]), ('CodeCatch', 'Google'), bbox_to_anchor=(1., 1.0325), loc=2, handletextpad=0.4)
ax.legend((rects1[0], rects2[0]), ('CodeCatch', 'Google'), loc = 1, handletextpad=0.4)

fig.tight_layout(pad=0.2)##0.1)

##fig.subplots_adjust(bottom=0.17, top=1)

plt.savefig(FIG_DIR + METRIC[2] + ".eps")
plt.savefig(FIG_DIR + METRIC[2] + ".pdf")

#plt.show()

