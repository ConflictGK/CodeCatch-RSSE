"""
Description:
This module downloads the 1000 most-starred repositories associated with Java
language from GitHub.

Limitations:
Maximum file size = 500MB
Maximum returned result pages = 10
Maximum repositories in each page = 100

Downloaded files are zip compressed
"""
import os
import requests
from properties import REPOS_PATH

MAX_FILE_SIZE = 5000000  # kB
REPO_PAGE_NUM = 10	  # number of result pages to download. (max per page = 100)
REPOS_PER_PAGE = 100
REJECT_REPO_NAMES = ['android']


def get_response(page_number):
	"""
	Sends request to retrieve a single page (out of 10) with most-starred repos.
	"""
	print("Sending request for GitHub most-starred repos...")
	response = requests.get(
		"https://api.github.com/search/repositories?q=java+language:java&sort=stars&order=desc"
		+ "&page=" + str(page_number) + "&per_page=" + str(REPOS_PER_PAGE))
	return response


def get_repo_info(response):
	"""
	Extracts information from request response regarding:
	(1) repository name (e.g. elasticsearch)
	(2) repository full name (e.g. elastic/elasticsearch)
	(3) repository content size
	"""
	print("Gathering repo names...")
	repo_names = []
	repo_full_names = []
	repo_sizes = []
	for index in range(REPOS_PER_PAGE):
		repo_names.append(response.json()["items"][index]["name"])
		repo_full_names.append(response.json()["items"][index]["full_name"])
		repo_sizes.append(response.json()["items"][index]["size"])
	return {
		"repo_names": repo_names,
		"repo_full_names": repo_full_names,
		"repo_sizes": repo_sizes
	}


def download_repo(repository_full_name, repo_size):
	"""
	Sends request to download repository content as zipball/tarball.
	If repository exceeds MAX_FILE_SIZE downloading process is aborted.
	"""
	print("Downloading repo:{} ... size: {} kB".format(repository_full_name, repo_size))
	if repo_size > MAX_FILE_SIZE:
		print("Repo exceeds maximum file size of {}. Aborting download...".format(MAX_FILE_SIZE))
		return None
	if any([name in repository_full_name.lower() for name in REJECT_REPO_NAMES]):
		print("Repo {} contains unwanted name. Aborting download...".format(repository_full_name))
		return None
	repository_data = requests.get("https://api.github.com/repos/"
								   + repository_full_name + "/zipball")
	return repository_data


def write_to_file(repo_name, repository_content=None):
	"""
	Writes the downloaded repo content in a given directory.
	"""
	if repository_content:
		print("Saving data...")
		with open(os.path.join(REPOS_PATH, repo_name + ".zip"), "wb") as file:
			file.write(repository_content.content)

if __name__ == "__main__":
	for page_num in range(1, REPO_PAGE_NUM + 1):
		print("Sending request to retrieve page {}...".format(page_num))
		resp = get_response(page_number=page_num)
		repo_info = get_repo_info(response=resp)
		for i, repo_full_name in enumerate(repo_info['repo_full_names']):
			print("Starting download-saving process for repo index: {}...".format(i))
			repo_content = download_repo(repository_full_name=repo_full_name,
										 repo_size=repo_info['repo_sizes'][i])
			write_to_file(repo_name=repo_info['repo_names'][i], repository_content=repo_content)
