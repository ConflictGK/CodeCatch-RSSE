import json
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import euclidean
from CLUSTERER.k_selector import select_k, tfidf_methodinvocations, multidimensional_scaling, clean_up_snippets
import sys
sys.path.append('../')

pd.options.mode.chained_assignment = None   # turn off chained assignment pandas warning


def kmeans_clustering(clean_snippets, K):
	"""
	Performs the final clustering based on the KMeans algorithm. The K is selected based on bunch of other methods
	For more info see select_k.py script. Finally, organizes data in a pandas DataFrame.
	:param snippet_data: Info of snippets retrieved by query and augmented by the mining done in previous stages
	:return: clustered_results_frame: DataFrame of the snippet info after KMeans clustering
	:return: term_freqs_by_cluster: DataFrame containing all the APIs and the weight of each API per cluster.
	"""
	# List of MethodInvocations sequences as comma separated strings
	mis = [snippet[0] for snippet in clean_snippets]

	# Snippets' code
	code = [snippet[1] for snippet in clean_snippets]

	# Snippets' url
	url = [snippet[2] for snippet in clean_snippets]

	# Snippets' url positions
	url_position = [snippet[3] for snippet in clean_snippets]

	# Snippets' in page order
	in_page_order = [snippet[4] for snippet in clean_snippets]

	api_qualified_names = [snippet[5] for snippet in clean_snippets]

	# Perform TFIDF transformation and retrieve the dissimilarity measure (cosine distance) of snippets
	dist, tfidf_matrix, terms = tfidf_methodinvocations(methodinvocations=mis)

	# Multidimensional Scaling to reduce to 2D
	X = multidimensional_scaling(distances=dist)

	# KMeans
	km = KMeans(n_clusters=K, init='k-means++', max_iter=1000, n_init=15, random_state=20)
	cluster_labels = km.fit_predict(X)

	# Calculate average silhouette score for all samples
	silhouette_avg = silhouette_score(X, cluster_labels, metric='cosine')
	print("For n_clusters = {}, average silhouette score = {:.2f}".format(K, silhouette_avg))

	# Calculate term frequencies (weights) per cluster
	term_freqs = pd.DataFrame(tfidf_matrix.toarray(), columns=terms)
	term_freqs['cluster'] = cluster_labels
	term_freqs_by_cluster = term_freqs.groupby('cluster').sum()

	# Calculate distances from cluster center
	centers = km.cluster_centers_
	dists_cluster_center = [euclidean(point, centers[label]) for point, label in zip(X, cluster_labels)]

	# Calculate number of API calls
	num_api_calls = [len(mis[i].split(',')) for i in range(len(clean_snippets))]

	# Calculate lines of code per snippet
	loc = [(c.count('\n') + 1) for c in code]

	# Calculate weight of API calls
	api_weights = []
	for mi, label in zip(mis, cluster_labels):
		method_list = set(mi.split(','))
		terms = term_freqs_by_cluster.iloc[label, :]
		weight = 0
		for method in method_list:
			if method.lower() in terms.index:
				weight += terms[method.lower()]

		api_weights.append(weight)

	# Organize results in a DataFrame
	results = {
		'MethodInvocations': mis,
		'API Qualified Names': api_qualified_names,
		'Code': code,
		'Url': url,
		'Url Position': url_position,
		'In Page Order': in_page_order,
		'Dist Center': dists_cluster_center,
		'Num API Calls': num_api_calls,
		'API Weights': api_weights,
		'LOC': loc,
		'Cluster': cluster_labels
	}
	clustered_results_frame = pd.DataFrame(results)

	return clustered_results_frame, term_freqs_by_cluster

def present_results(pp, results, term_freqs):
	finalresult = {}
	
	num_snippets_per_cluster = results['Cluster'].value_counts()  # Number of snippets per cluster
	num_clusters = len(num_snippets_per_cluster)  # Number of clusters
	
	finalresult["num_snippets_per_cluster"] = [int(i) for i in num_snippets_per_cluster]
	finalresult["num_clusters"] = len([i for i in num_snippets_per_cluster])
	finalresult["clusters"] = []
	
	# Separate snippets based on their cluster label
	snippet_clusters = [results.loc[results['Cluster'] == i] for i in range(num_clusters)]

	# Re-rank inter-cluster snippets based on their score and scale them in range[0, 1], descending order
	scaler = MinMaxScaler(feature_range=(0, 1))
	for cluster in snippet_clusters:
		cluster.sort_values(by='Dist Center', ascending=True, inplace=True)
		cluster['Score'] = 1 - scaler.fit_transform(cluster['Dist Center'].values.reshape(-1, 1))

		snippets = json.loads(cluster.to_json(orient='records'))
		for i, _ in enumerate(snippets):
			snippets[i]["API_Weights"] = snippets[i].pop("API Weights")
			snippets[i]["API_Qualified_Names"] = snippets[i].pop("API Qualified Names")
			snippets[i]["Url_Position"] = snippets[i].pop("Url Position")
			snippets[i]["In_Page_Order"] = snippets[i].pop("In Page Order")
			snippets[i]["Num_API_Calls"] = snippets[i].pop("Num API Calls")
			snippets[i]["Dist_Center"] = snippets[i].pop("Dist Center")
			snippets[i]["MethodInvocations"] = snippets[i].pop("MethodInvocations").split(',')

		finalresult["clusters"].append({
			"cluster_snippets": snippets
		})

	for i in range(len(term_freqs)):
		avg_cluster_api_weights = snippet_clusters[i]['API Weights'].mean()
		finalresult["clusters"][i]["avg_cluster_api_weights"] = avg_cluster_api_weights
		top_apis_by_cluster = term_freqs.iloc[i, :].sort_values(ascending=False).index[0:8].values
		finalresult["clusters"][i]["top_apis_by_cluster"] = top_apis_by_cluster.tolist()

	with open(pp.RESULTS_D, 'w') as outfile:
		outfile.write(json.dumps(finalresult, indent = 3))

def run_clustering(pp):
	# Load query data file
	with open(pp.RESULTS_C, 'r') as datafile:
		data = json.load(datafile)

	# Filter duplicates and snippets with low similarity
	clean_snippets = clean_up_snippets(data)
	print("Snippets after deleting duplicates/similars = {}".format(len(clean_snippets)))

	# Select number of clusters for KMeans
	K = select_k(pp, clean_snippets)

	clustered_data, cluster_term_freqs = kmeans_clustering(clean_snippets, K)

	present_results(pp, results=clustered_data, term_freqs=cluster_term_freqs)

if __name__ == "__main__":
	run_clustering()
