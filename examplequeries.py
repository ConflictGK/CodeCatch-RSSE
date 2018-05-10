import os

class ExampleResults:
	def __init__(self, cwd):
		self.example_queries = []
		self.EXPERIMENTS_DIR = cwd + os.path.sep + "experiments" + os.path.sep
	
	def read_example_queries(self):
		if not self.example_queries:
			self.example_queries = []
			with open(self.EXPERIMENTS_DIR + "queries.txt") as infile:
				for line in infile:
					line = line.strip()
					if line:
						self.example_queries.append(line)
		return self.example_queries

	def is_example_query(self, query):
		return query in self.example_queries

	def get_example_query_index(self, query):
		return self.example_queries.index(query)
