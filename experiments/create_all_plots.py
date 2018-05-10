import os
import json
from properties import Properties
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

FIG_DIR = "C:/Users/themis/Desktop/RAISE2018/images/" if os.path.exists("C:/Users/themis/Desktop/RAISE2018/images/") else "C:/Users/user/Desktop/RAISE2018/images/"

def plot_silhouette_full(X, n_clusters, sample_silhouette_values, y_lower, silhouette_avg, cluster_labels, centers):
	# Create a subplot with 1 row and 2 columns
	fig, (ax1, ax2) = plt.subplots(1, 2)
	fig.set_size_inches(18, 7)

	ax1.set_xlim([-0.1, 1])
	ax1.set_ylim([0, X.shape[0] + (n_clusters + 1) * 10])

	for i in range(n_clusters):
		ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]
		ith_cluster_silhouette_values.sort()
		size_cluster_i = ith_cluster_silhouette_values.shape[0]
		y_upper = y_lower + size_cluster_i

		color = cm.spectral(float(i) / n_clusters)
		ax1.fill_betweenx(np.arange(y_lower, y_upper),
						  0, ith_cluster_silhouette_values,
						  facecolor=color, edgecolor=color, alpha=0.7)

		# Label the silhouette plots with their cluster numbers at the middle
		ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

		# Compute the new y_lower for next plot
		y_lower = y_upper + 10  # 10 for the 0 samples

	ax1.set_xlabel("The silhouette coefficient values", size=20)
	ax1.set_ylabel("Cluster label", size=20)

	# The vertical line for average silhouette score of all the values
	ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

	ax1.set_yticks([])  # Clear the yaxis labels / ticks
	ax1.set_xticks(np.arange(-1, 1.2, 0.2))
	ax1.tick_params(labelsize=16)

	# 2nd plot showing the actual clusters formed (after MDS to 2D)
	colors = cm.spectral(cluster_labels.astype(float) / n_clusters)
	ax2.scatter(X[:, 0], X[:, 1], marker='o', s=30, lw=0, alpha=0.7,
				c=colors, edgecolor='k')

	# Labeling the clusters

	# Draw white circles at cluster centers
	ax2.scatter(centers[:, 0], centers[:, 1], marker='o',
				c="white", alpha=1, s=200, edgecolor='k')

	for i, c in enumerate(centers):
		ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1,
					s=50, edgecolor='k')

	ax2.set_xlabel("Feature space for the 1st feature", size=18)
	ax2.set_ylabel("Feature space for the 2nd feature", size=18)
	ax2.tick_params(labelsize=16)

	plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
				  "with n_clusters = %d" % n_clusters),
				 fontsize=16, fontweight='bold')

	plt.show()

def plot_silhouette(X, n_clusters, sample_silhouette_values, y_lower, silhouette_avg, cluster_labels, centers):
	# Create a subplot with 1 row and 2 columns
	fig, ax1 = plt.subplots(1, 1)
	fig.set_size_inches(4.2, 2.65)

	for i in range(n_clusters):
		ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]
		ith_cluster_silhouette_values.sort()
		size_cluster_i = ith_cluster_silhouette_values.shape[0]
		y_upper = y_lower + size_cluster_i

		color=(56/255, 83/255, 164/255)#cm.spectral(float(i) / n_clusters)
		ax1.fill_betweenx(np.arange(y_lower, y_upper),
						  0, ith_cluster_silhouette_values,
						  facecolor=color, edgecolor=color, 
						  alpha=0.7)

		# Label the silhouette plots with their cluster numbers at the middle
		ax1.text(-0.25, y_lower + 0.5 * size_cluster_i - 3, "Cluster " + str(i + 1))

		# Compute the new y_lower for next plot
		y_lower = y_upper + 10  # 10 for the 0 samples

	ax1.set_xlabel("Silhouette Coefficient Values")#, size=20)
	ax1.set_ylabel("Cluster Label")#, size=20)

	#ax1.set_xlim(xmin=-0.1, xmax=1)
	#ax1.set_ylim([0, X.shape[0] + (n_clusters + 1) * 10])

	# The vertical line for average silhouette score of all the values
	ax1.axvline(x=silhouette_avg, color="black", linestyle="--")

	ax1.set_yticks([])  # Clear the yaxis labels / ticks
	#ax1.set_xticks(np.arange(-1, 1.2, 0.2))
	#ax1.tick_params(labelsize=16)
	fig.tight_layout(pad=0.2)

	fig.subplots_adjust(left=0.1, right=0.9)

	plt.savefig(FIG_DIR + "silhouette.eps")
	plt.savefig(FIG_DIR + "silhouette.pdf")
	#plt.show()

def plot_all_silhouette(num_clusters, silhouette_values):
	fig, ax1 = plt.subplots(1, 1)
	fig.set_size_inches(4.2, 2.65)
	ax1.plot(num_clusters, silhouette_values, '-s', color=(56/255, 83/255, 164/255))
	ax1.set_xlabel('Number of Clusters')
	ax1.set_ylabel('Average Silhouette Values')
	ax1.set_ylim([0.52, 0.78])
	fig.tight_layout(pad=0.2)
	plt.savefig(FIG_DIR + "silhouetteFull.eps")
	plt.savefig(FIG_DIR + "silhouetteFull.pdf")
	#plt.show()
	#exit()

def load_data(ress):
	with open(ress) as infile:
		alldata = json.load(infile)
	alldata_new = {}
	for n_clusters in alldata:
		alldata_new[n_clusters] = {}
		alldata_new[n_clusters]["X"] = np.array(alldata[n_clusters]["X"])
		alldata_new[n_clusters]["n_clusters"] = alldata[n_clusters]["n_clusters"]
		alldata_new[n_clusters]["sample_silhouette_values"] = np.array(alldata[n_clusters]["sample_silhouette_values"])
		alldata_new[n_clusters]["y_lower"] = alldata[n_clusters]["y_lower"]
		alldata_new[n_clusters]["silhouette_avg"] = alldata[n_clusters]["silhouette_avg"]
		alldata_new[n_clusters]["cluster_labels"] = np.array(alldata[n_clusters]["cluster_labels"])
		alldata_new[n_clusters]["centers"] = np.array(alldata[n_clusters]["centers"])
	return alldata_new

PARENT_DIR = Properties(0).PARENT_DIR
ress = PARENT_DIR + "query0/resultsS.json"

alldata = load_data(ress)
num_clusters = [n_clusters for n_clusters in alldata]
silhouette_values = [alldata[n_clusters]["silhouette_avg"] for n_clusters in alldata]
optimal_num_clusters = num_clusters[silhouette_values.index(max(silhouette_values))]
plot_all_silhouette(num_clusters, silhouette_values)

plot_silhouette(alldata[optimal_num_clusters]["X"], 
				alldata[optimal_num_clusters]["n_clusters"], 
				alldata[optimal_num_clusters]["sample_silhouette_values"], 
				alldata[optimal_num_clusters]["y_lower"], 
				alldata[optimal_num_clusters]["silhouette_avg"], 
				alldata[optimal_num_clusters]["cluster_labels"], 
				alldata[optimal_num_clusters]["centers"])
