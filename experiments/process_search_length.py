import os
import json
import matplotlib.pyplot as plt

FIG_DIR = "C:/Users/themis/Desktop/RAISE2018/images/" if os.path.exists("C:/Users/themis/Desktop/RAISE2018/images/") else "C:/Users/user/Desktop/RAISE2018/images/"

def search_length(examined_results, num_relevant_results_required, max_number=15):
	result_number = 0
	number_of_irrelevant_results = 0
	for res in examined_results:
		if res == 1:
			result_number += 1
			if result_number == num_relevant_results_required:
				return number_of_irrelevant_results
		else:
			number_of_irrelevant_results += 1
	return max_number

queries = []
with open("queries.txt") as infile:
	for line in infile:
		line = line.strip()
		if line:
			queries.append(line)

with open("alldata.json") as infile:
	alldata = json.load(infile)

codecatch_sl = []
google_sl = []

ind = list(range(1, 16))
results_to_keep = 15
for query in ["query" + str(query_id) for query_id in range(len(queries))]:
	codecatch_snippets = alldata["codecatch"][query][:results_to_keep]
	google_snippets = alldata["google"][query][:results_to_keep]
	codecatch_sl.append([search_length(codecatch_snippets, i) for i in ind])
	google_sl.append([search_length(google_snippets, i) for i in ind])

codecatch_msl = [sum([c[i - 1] for c in codecatch_sl]) / len([c[i - 1] for c in codecatch_sl]) for i in ind]
google_msl = [sum([c[i - 1] for c in google_sl]) / len([c[i - 1] for c in google_sl]) for i in ind]

fig, ax = plt.subplots()
fig.set_size_inches(4.5, 3.0)
rects1 = ax.plot(ind, codecatch_msl, 'b-')
rects2 = ax.plot(ind, google_msl, 'r--')

ax.set_ylim([0, 14.8])
ax.set_xlim([0, 15.5])
ax.set_xticks(range(16))
ax.set_yticks(range(15))
ax.set_ylabel('# Irrelevant Results to View')
ax.set_xlabel('# Relevant Results Required')

ax.legend((rects1[0], rects2[0]), ('CodeCatch', 'Google'), handletextpad=0.5)

fig.tight_layout()

#fig.subplots_adjust(left=0.1, right=0.9)

plt.savefig(FIG_DIR + "searchlength.eps")
plt.savefig(FIG_DIR + "searchlength.pdf")

plt.show()
