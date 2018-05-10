# -*- coding: utf-8 -*-
import scrapy
import re
import time

from Downloader.htmlcleanser import MLStripper
from Downloader.spiders import google

QUERY_PATTERN = " java (import OR class OR interface OR public OR \
	protected OR private OR abstract OR final OR static OR if OR \
	for OR void OR int OR long OR double)"

RE_LOC_NUM_PATTERN = '\\n\s*[0-9]+\s'


class GooglesnippetsSpider(scrapy.Spider):
	name = "googlesnippets"
	allowed_domains = []
	start_urls = []
	query = None

	def __init__(self, query=None):
		self.query = query
		retrieved_urls = google.search(query + QUERY_PATTERN, stop=40, pause=0.1, num=40)
		self.start_urls = [url for url in retrieved_urls]

	def url_position(self, response):
		"""
		Url Position.
		The rank (the first page has rank 1, and so on) of the web page where the snippet
		is extracted.
		"""
		# If response got redirected check the position of the original url
		if 'redirect_urls' in response.request.meta:
			url_position = self.start_urls.index(response.request.meta['redirect_urls'][0])
		else:
			url_position = self.start_urls.index(response.url)
		# return index + 1 because of zero indexing
		return (url_position + 1)

	def first_second_third_url(self, response):
		"""
		First/Second/Third Url.
		True if the snippet is from the web page of rank 1/2/3; False otherwise
		"""
		# If response got redirected check the position of the original url
		if 'redirect_urls' in response.request.meta:
			url_position = self.start_urls.index(response.request.meta['redirect_urls'][0])
		else:
			url_position = self.start_urls.index(response.url)
		if url_position <= 2:
			return True
		else:
			return False

	def first_in_page(self, index):
		"""
		First in-page.
		True if the snippet appears as the first snippet from the web page.
		"""
		if index == 0:
			return True
		else:
			return False

	def accepted_answer(self, answer):
		"""
		Accepted answer.
		True if the snippet belongs in accepted answer(e.g. in stackoverflow).
		"""
		if answer.xpath('.//*[contains(@class, "vote-accepted-on")]'):
			return True
		else:
			return False

	def answer_votes(self, answer):
		"""
		Answer's votes.
		Return the votes of the answer (e.g. in stackoverflow).
		"""
		if answer.xpath('.//*[contains(@class, "vote-count-post")]/text()'):
			return answer.xpath('.//*[contains(@class, "vote-count-post")]/text()').extract_first()
		else:
			return 0

	def answer_stars(self, response):
		"""
		Answer's stars.
		Return the starts of the answer (e.g. in GitHub Gists)
		"""
		if response.xpath('.//*[contains(@class, "social-count")]/text()'):
			return response.xpath('.//*[contains(@class, "social-count")]/text()').extract_first().strip()
		else:
			return 0

	def form_data(self, response, answer, index, cell=None):
		"""
		Organize data in dictionary form.
		"""
		if cell:
			code = cell.extract()
		else:
			code = answer.extract()
		d = {
			'code': code,
			'in_page_order': index + 1,
			'first_in_page': self.first_in_page(index),
			'accepted_answer': self.accepted_answer(answer),
			'answer_votes': self.answer_votes(answer),
			'answer_stars': self.answer_stars(response)
		}
		return d

	def filter_loc_numbers(self, string):
		"""
		Filter out line of code numbering in retrieved snippets.
		Regex Pattern: \\n\s*[0-9]+\s
		Regex Explanation: Line numbering usually starts in a new line, followed by 1 or more whitespaces,
		by 1 or more digits showning the number of line, and by at least a white space before actual code starts
		"""
		return re.sub(RE_LOC_NUM_PATTERN, '\n', string)

	def parse(self, response):
		"""
			After some little research code in websites appears in the following tags. Order is based on
			frequency of appearence in specific tag.
			(1) pre, (2) code, (3) crayon-pre
		"""
		# For each snippet found in a website extract: (1) code, (2) the order of appearence in the
		# specific website (in_page_order), (3) if it's the first snippet in the website (first_in_page)
		t0 = time.time()
		segments = []
		if 'stackoverflow' in response.url:
			# Select only code from answers in stackoverflow 
			answers = response.xpath('//*[contains(@id, "answer-")]')
			for i, answer in enumerate(answers):
				# one post in StackOverflow may contain multiple snippets (cells)
				cells = answer.xpath('.//pre')
				for cell in cells:  # one post in StackOverflow may contain multiple snippets.
					segments.append(self.form_data(response=response, answer=answer, index=i, cell=cell))
		elif 'github.com' in response.url:
			if response.xpath('//*[contains(@id, "LC")]'):
				answers = response.xpath('//*[contains(@id, "LC")]')
				for i, answer in enumerate(answers):
					segments.append(self.form_data(response=response, answer=answer, index=i))
		elif 'javascript' in response.url:
			pass	# avoid responses that refer to javascript
		elif response.xpath('//pre'):
			answers = response.xpath('//pre')
			t0 = time.time()
			for i, answer in enumerate(answers):
				if time.time() - t0 > 1:   # interrupt crawling for current website if it takes long
					break
				segments.append(self.form_data(response=response, answer=answer, index=i))
		elif response.xpath('//*[contains(@class, "crayon-pre")]'):
			answers = response.xpath('//*[contains(@class, "crayon-pre")]')
			t0 = time.time()
			for i, answer in enumerate(answers):
				if time.time() - t0 > 1:   # interrupt crawling for current website if it takes long
					break
				segments.append(self.form_data(response=response, answer=answer, index=i))

		# avoid scraping websites with too many segments because most probably
		# they contain just signatures of methods or redundant stuff
		if len(segments) < 50:
			for segment in segments:
				s = MLStripper()
				segment['code'] = ''.join(segment['code'])
				s.feed(segment['code'].encode('ascii', 'ignore').decode('ascii', 'ignore'))
				code_data = s.get_data()
				code_data = self.filter_loc_numbers(string=code_data)
				segment['code'] = code_data
				# This flag (length) indicates if the retrieved snippet is
				# between 100 and 2500 chars in length (True) or less (False)
				if 100 < len(code_data) < 2500:
					segment['length'] = True
				else:
					segment['length'] = False

				# This flag (semicolon) indicates if the semicolon java
				# special character appears in data retrieved.
				if ';' in code_data:
					segment['semicolon'] = True
				else:
					segment['semicolon'] = False
		else:
			for segment in segments:
				# Set these values to False in order to be ignored by next steps
				segment['length'] = False
				segment['semicolon'] = False

		yield {
			'query': self.query,
			'url': response.url,
			'url position': self.url_position(response),
			'segments': segments,
		}
