from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
import json

def clean_up_snippets(data):
	snippets = []   # list of tuples ---> (methods, code, url, url_position, in_page_order)

	for website in data:
		for segment in sorted(website['segments'], reverse = True, key=lambda x: x['API_Ratio']):
			# Clean up APIs
			#apis = {}
			#for s, j in segment['APIs'].items():
			#	if '__init__' not in s:
			#		apis[s] = j
			#segment['APIs'] = apis

			# Remove snippets that are very large
			if len(segment['code'].split('\n')) > 200:
				continue

			# Remove snippets with fewer than 1 API calls
			if len(segment['APIs']) > 1:# and segment['readability']:
				methods = ','.join(set([key for key in segment['APIs'].keys()]))
				code = segment['code']
				url = website['url']
				url_position = website['url position']
				in_page_order = segment['in_page_order']
				api_qualified_names = segment['APIsQualifiedNames']
				snippets.append((methods, code, url, url_position, in_page_order, api_qualified_names))

	return snippets


def tfidf_methodinvocations(methodinvocations):
	"""
	Performs TFIDF transformation on snippets based on their MethodInvocations and
	calculates the distances (cosine) from the TFIDF matrix
	:param methodinvocations: The MethodInvocations for each snippet given as comma separated string
	:return: distances: Cosine distances after TFIDF transformation.
			 tfidf_matrix : MxN matrix when M is the number of samples(snippets), N is the number of TFIDF features.
			 terms: The features used in TFIDF matrix. This is a vocabulary.
	"""
	# Initialize the TFIDF vectorizer
	exclude_mis = ['println', 'printStackTrace']	 # Exclude these MethodInvocations
	tfidf_vectorizer = TfidfVectorizer(max_df=0.8, tokenizer=lambda s: s.split(), stop_words=exclude_mis)
	tfidf_matrix = tfidf_vectorizer.fit_transform(methodinvocations)
	terms = tfidf_vectorizer.get_feature_names()
	distances = 1 - cosine_similarity(tfidf_matrix)	 # TODO: Experiment with different distances

	return distances, tfidf_matrix, terms


def multidimensional_scaling(distances):
	"""
	Performs Multidimensional Scaling to reduce distances matrix from N dimensions to 2D
	:param distances: Cosine distances after TFIDF transformation
	:return: The positions of samples on 2D-Plane
	"""
	mds = MDS(n_components=2, dissimilarity='precomputed', random_state=1)
	pos = mds.fit_transform(distances)

	return pos


def silhouette_analysis(pp, snippets):
	"""
	Performs silhouette analysis on KMeans to estimate a good number of clusters.
	Criteria to chose a good K:
		(1) Overall decent individual silhouette score for each cluster
		(2) Good average silhouette score for entire clustering
	:param snippets: The snippets to be clustered
	:param command_line_args: Command line arguments given by user while executing script.
	:return: The best candidate K according to silhouette analysis
	"""
	# List of MethodInvocations sequences as comma separated strings
	mis = [snippet[0] for snippet in snippets]
	# Perform TFIDF transformation and retrieve the dissimilarity measure (cosine distance) of snippets
	dist, _, _ = tfidf_methodinvocations(methodinvocations=mis)

	# Multidimensional Scaling to reduce to 2D
	X = multidimensional_scaling(distances=dist)

	range_n_clusters = range(2, min(9, len(snippets) - 1))
	candidate_n_clusters = []	# list of tuples with K's that have good silhouettes (K, silhouette_avg for that K)

	alldata = {}
	for n_clusters in range_n_clusters:
		clusterer = KMeans(n_clusters=n_clusters, init='k-means++', random_state=20)
		cluster_labels = clusterer.fit_predict(X)

		silhouette_avg = silhouette_score(X, cluster_labels, metric='cosine')

		sample_silhouette_values = silhouette_samples(X, cluster_labels, metric='cosine')

		y_lower = 10
		for i in range(n_clusters):
			# Aggregate the silhouette scores for samples belonging to cluster i, and sort them
			ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]
			ith_cluster_silhouette_values.sort()	# ascending

			candidate_n_clusters.append((n_clusters, silhouette_avg))

		centers = clusterer.cluster_centers_
		alldata[n_clusters] =  {"X": X.tolist(), "n_clusters": n_clusters, "sample_silhouette_values": sample_silhouette_values.tolist(), "y_lower": y_lower,
								"silhouette_avg": float(silhouette_avg), "cluster_labels": cluster_labels.tolist(), "centers": centers.tolist()}

	with open(pp.RESULTS_S, 'w') as outfile:
		outfile.write(json.dumps(alldata, indent = 3))

	# Find and return the best K from candidates
	candidate_n_clusters.sort(key=lambda x: x[1])
	return candidate_n_clusters[-1][0]


def select_k(pp, snippets):
	"""
	Selects a good K to be used for clustering algorithms that require it as ground truth.
	The selection is based on one of the following algorithms individually or as the most common result of all of them:
	(1) Hierarchical Clustering
	(2) Elbow Method
	(3) Silhouette Analysis
	(4) Affinity Propagation
	:param snippets: The data as read from the json file containing the snippet info.
	:param command_line_args: Command line arguments given by user while executing script.
	:return: The selected K
	"""
	# Remove duplicates and unfamiliar snippets from data
	print("Estimating number of clusters based on Silhouette Analysis...")
	k_silhouette = silhouette_analysis(pp, snippets)
	print("Silhouette Analysis = {}".format(k_silhouette))
	return k_silhouette
