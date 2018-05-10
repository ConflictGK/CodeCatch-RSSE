import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import normalize
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import GridSearchCV


def plot_f1_score(df1, ax, algorithm):
	df2 = pd.DataFrame(df1.loc[:, ['param_learning_rate',
								   'param_n_estimators',
								   'mean_test_score']])
	for i in range(1, 11):
		df3 = pd.DataFrame(df2.query('param_learning_rate=={}'.format(i)))
		df4 = df3.drop('param_learning_rate', axis=1)
		ests = pd.Series(df4['param_n_estimators'])
		scores = pd.Series(df4['mean_test_score'])
		df5 = pd.DataFrame(scores)
		df5.set_index(ests, inplace=True)

		ax.plot(df5, marker='o')
	ax.legend(list(range(1, 11)))
	ax.set_title("F1 Scores for variate learning rate and {} as criterion.".format(algorithm),
				 fontweight="bold", size=20)
	ax.set_xlabel("Number of estimators.", size=15)
	ax.set_ylabel("Average F-Measure Score.", size=15)


def plot_recall_score(df1, ax, algorithm):
	df2 = pd.DataFrame(df1.loc[:, ['param_min_samples_leaf',
								   'param_n_estimators',
								   'mean_test_score']])
	for i in range(1, 11):
		df3 = pd.DataFrame(df2.query('param_min_samples_leaf=={}'.format(i)))
		df4 = df3.drop('param_min_samples_leaf', axis=1)
		ests = pd.Series(df4['param_n_estimators'])
		scores = pd.Series(df4['mean_test_score'])
		df5 = pd.DataFrame(scores)
		df5.set_index(ests, inplace=True)

		ax.plot(df5, marker='o')
	ax.legend(list(range(1, 11)))
	ax.set_title("Recall Scores for variate min_samples_leaf and {} as criterion.".format(crit),
				 fontweight="bold", size=20)
	ax.set_xlabel("Number of estimators.", size=15)
	ax.set_ylabel("Average Recall Score.", size=15)


def plot_precision_scores(df1, ax, algorithm):
	df2 = pd.DataFrame(df1.loc[:, ['param_min_samples_leaf',
								   'param_n_estimators',
								   'mean_test_score']])
	for i in range(1, 11):
		df3 = pd.DataFrame(df2.query('param_min_samples_leaf=={}'.format(i)))
		df4 = df3.drop('param_min_samples_leaf', axis=1)
		ests = pd.Series(df4['param_n_estimators'])
		scores = pd.Series(df4['mean_test_score'])
		df5 = pd.DataFrame(scores)
		df5.set_index(ests, inplace=True)

		ax.plot(df5, marker='o')
	ax.legend(list(range(1, 11)))
	ax.set_title("Precision Scores for variate min_samples_leaf and {} as criterion.".format(crit),
				 fontweight="bold", size=20)
	ax.set_xlabel("Number of estimators.", size=15)
	ax.set_ylabel("Average Precision Score.", size=15)


if __name__ == "__main__":
	data = pd.read_csv('code_metrics_dataset.csv')

	X = data.iloc[:, 0:25]
	print("X shape = {}".format(X.shape))
	y = data.iloc[:, 25]
	print("y shape = {}".format(y.shape))

	X_norm = normalize(X)
	X = pd.DataFrame(X_norm)

	adaboost = AdaBoostClassifier()

	# create the parameters grid
	param_grid = {
		'n_estimators': list(range(20, 160, 10)),
		'learning_rate': list(np.arange(0.1, 2.1, 0.05))
	}

	# instantiate the grid
	grid_f1 = GridSearchCV(adaboost, param_grid, cv=10, scoring='f1', verbose=1)
	grid_recall = GridSearchCV(adaboost, param_grid, cv=10, scoring='recall', verbose=1)
	grid_precision = GridSearchCV(adaboost, param_grid, cv=10, scoring='precision', verbose=1)

	# fit the randomizers with data
	grid_f1.fit(X, y)
	grid_recall.fit(X, y)
	grid_precision.fit(X, y)

	# create a list of the mean scores only
	mean_f1 = grid_f1.cv_results_['mean_test_score']
	mean_recall = grid_recall.cv_results_['mean_test_score']
	mean_precision = grid_precision.cv_results_['mean_test_score']

	fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(25, 10))

	f1_scores_samme = pd.DataFrame(grid_f1.cv_results_)
	f1_scores_samme = f1_scores_samme.query("param_algorithm=='SAMME'")
	plot_f1_score(f1_scores_samme, ax1, 'SAMME')