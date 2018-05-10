import os

class Properties:
	def __init__(self, query, example_query_index = -1, thepath = None):
		self.query = query
		main_dir = os.getcwd()
		self.SCRAPY_EXEC = "C:/WinPython36/python-3.6.3.amd64/Scripts/scrapy.exe"
		self.PARENT_DIR = main_dir + os.path.sep
		if example_query_index >= 0:
			self.DATA_DIR = self.PARENT_DIR + "experiments" + os.path.sep + "query" + str(example_query_index) + os.path.sep
		else:
			if thepath and thepath != "None":
				self.DATA_DIR = self.PARENT_DIR + "data" + os.path.sep + thepath + os.path.sep
			else:
				self.DATA_DIR = self.PARENT_DIR + "data" + os.path.sep
		self.SRESULTS_A = self.DATA_DIR[:-1].split(os.path.sep)[-2] + os.path.sep + self.DATA_DIR[:-1].split(os.path.sep)[-1] + os.path.sep + 'resultsA.json'
		self.RESULTS_A = self.DATA_DIR + 'resultsA.json'
		self.RESULTS_B = self.DATA_DIR + 'resultsB.json'
		self.RESULTS_C = self.DATA_DIR + 'resultsC.json'
		self.RESULTS_D = self.DATA_DIR + 'resultsD.json'
		self.RESULTS_S = self.DATA_DIR + 'resultsS.json'
		self.QUERY_DATA_FILE = self.RESULTS_A
		self.RESULTS_FILE = self.RESULTS_D
