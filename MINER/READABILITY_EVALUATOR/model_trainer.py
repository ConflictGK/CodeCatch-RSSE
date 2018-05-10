"""
Description:
This module instantiates a Random Forest Classifier estimator and
saves it to disk for making predictions later.
"""
import logging
import time
import pandas as pd
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import normalize

logging.basicConfig(
	format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

TRAIN_DATAFILE = 'code_metrics_dataset.csv'

# Tuned hyper-parameters for RandomForest after GridSearch:
#   n_estimators = 40
#   criterion = 'entropy'
#   min_samples_leaf = 3
#   rest of parameters left to default values
RF_CRIT = 'entropy'
RF_MIN_SAMPLES_LEAF = 3
RF_N_ESTS = 40

# Tuned hyper-parameters for KNN after GridSearch:
#   n_neighbors = 11
#   weights='distance'
#   metric='cityblock'
KNN_N_NEIGHBORS = 11
KNN_WEIGHTS = 'distance'
KNN_METRIC = 'cityblock'

# Tuned hyper-parameters for AdaBoost after GridSearch:
#   n_estimators = 160
#   learning_rate = 0.6
#   algorithm = 'SAMME.R'
ADABOOST_N_ESTS = 160
ADABOOST_LEARN_RATE = 0.6
ADABOOST_ALGORITHM = 'SAMME.R'

def init_rf_estimator():
	"""
	Instantiate a Random forest estimator with the optimized hyper-parameters.
	:return: The RandomForest estimator instance.
	"""
	rf = RandomForestClassifier(
		criterion=RF_CRIT,
		min_samples_leaf=RF_MIN_SAMPLES_LEAF,
		max_features='auto',
		n_estimators=RF_N_ESTS,
		n_jobs=-1)
	return rf


def init_knn_estimator():
	"""
	Instantiate a KNN estimator with the optimized hyper-parameters.
	:return: The KNN estimator instance.
	"""
	knn = KNeighborsClassifier(
		n_neighbors=KNN_N_NEIGHBORS,
		weights=KNN_WEIGHTS,
		metric=KNN_METRIC
	)
	return knn


def init_adaboost_estimator():
	adaboost = AdaBoostClassifier(
		n_estimators=ADABOOST_N_ESTS,
		learning_rate=ADABOOST_LEARN_RATE,
		algorithm=ADABOOST_ALGORITHM
	)
	return adaboost


if __name__ == "__main__":
	# Load training data
	data = pd.read_csv(TRAIN_DATAFILE)
	X = data.iloc[:, 0:25]  # X.shape (training data)  --> (100, 25)
	y = data.iloc[:, 25]  # y.shape (targets)		--> (100,)

	# Normalize training data and organize them in pandas.DataFrame
	X = normalize(X)
	X = pd.DataFrame(X)

	# Instantiate Random Forest Classifier
	rf_clf = init_rf_estimator()

	# Instantiate KNN Classifier
	knn_clf = init_knn_estimator()

	# Instantiate AdaBoost Classifier
	adaboost_clf = init_adaboost_estimator()

	# Train the classifiers
	print("Training Random Forest Classifier...")
	t0 = time.time()
	rf_clf.fit(X, y)
	print("Training of Random Forest Classifier took {} seconds...".format(time.time() - t0))

	print("Training KNN classifier...")
	t0 = time.time()
	knn_clf.fit(X, y)
	print("Training of KNN Classifier took {} seconds...".format(time.time() - t0))

	print("Training AdaBoost Classifier...")
	t0 = time.time()
	adaboost_clf.fit(X, y)
	print("Training of AdaBoost Classifier took {} seconds...".format(time.time() - t0))

	# Save the trained model to disk for later use
	print("Saving Random Forest Classifier to local directory...")
	joblib.dump(rf_clf, 'RandomForestClassifier.pkl')
	print("Saving KNN Classifier to local directory...")
	joblib.dump(knn_clf, 'KNNClassifier.pkl')
	print("Saving AdaBoost Classifier to local directory...")
	joblib.dump(adaboost_clf, 'AdaBoostClassifier.pkl')