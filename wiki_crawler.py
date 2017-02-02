"""

@author: Varun Sharma

This program takes any random article on Wikipedia and clicks on the first link on the body
that is not within parenthesis or italicized.

This process when repeated subsequently ends up on the Philosophy Wikipedia page.

Returns as printed output:
    Print the Iteration number.
    Prints the path followed by clicking the first valid link.
    Prints the percentage of pages often lead to philosophy towards the end of the program.

Creates a Histogram plot of the distribution of path lengths for 500 different Wikipedia pages,
discarding the ones that never reach the Philosophy page.

"""

import re
import urllib.request
import numpy as np
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup

MAX_ITER = 500
MAX_TOLERANCE = 100
OUT_FILE = 'out.png'

class Wikipedia_Crawler:
    """Wikipedia Crawler"""
    def __init__(self):
        self.dict = {}

    def check_link(self, link, links_para):
        """
        Checks the validity of the link.
        """
        href  = link['href']
        if not href.startswith('/wiki/') or href == '/wiki/Latin' or href.startswith('#'):
            return False
        if "<i>" in link or href in links_para:
            return False
        title = href[6:]
        if title.startswith('Help:') or title.startswith('File:') or title.endswith('.ogg') or title.startswith('Wikipedia:'):
            return False
        return True

    def check_paragraph(self, para, links_para):
        """
        Checks the validity of a paragraph.
        """
        #Return False if no paragraphs found
        if para is None:
            return False

        links = para.find_all('a')
        #Return False if no links found
        if links is None:
            return False

        #Return True if one link is valid in the paragraph
        for link in links:
            if self.check_link(link, links_para):
                return True
        return False

    def get_first_link(self, article):
        """
        Retrieves the first valid URL from the current Wikipedia link.
        """
        #Hit the article Wikipeadia URL
        page = urllib.request.urlopen(article)
        html = page.read()
        soup = BeautifulSoup(html, 'lxml')

        #Iterate over all the paragraphs on that page to find the first valid link
        for child_para in soup.find_all('p'):
            links_para = str(re.findall('\((.*?)\)', str(child_para)))
            if self.check_paragraph(child_para, links_para):
                for child_link in child_para.find_all('a'):
                    if self.check_link(child_link, links_para):
                        #Return the next child link
                        return 'https://en.wikipedia.org' + child_link['href']

    def find_philosophy(self):
        '''
        The driver - Starts from a random Wikipedia URL and iterates until it reaches the Philosophy page (500 iterations).
        '''
        final_count = 0
        for i in range(0, MAX_ITER):
            print("### Iteration", i,"###")
            #Generate the next random Wikipedia link
            starting_article = urllib.request.urlopen('https://en.wikipedia.org/wiki/Special:Random').geturl()
            #Initialize/Reset variables 
            num_articles = 0
            articles = [starting_article]
            philosophy = False
            curr_article = starting_article           
            
            try:
                #Break if a page is stuck in infinite loop, break after 100 iterations
                while num_articles <= MAX_TOLERANCE:
                    num_articles += 1
                    first_link = self.get_first_link(curr_article)
                    #Break if no links found on the page.
                    if first_link is None:
                        print("No links found for ", curr_article['title'])
                        break
                    print(first_link[30:])
                    if first_link not in articles:
                        articles.append(first_link)
                        #Break if Philosophy Wikipedia page is reached.
                        if first_link == 'https://en.wikipedia.org/wiki/Philosophy':
                            final_count += 1
                            philosophy = True
                            break
                    curr_article = first_link
                #Store distribution in a dictionary
                if philosophy is True:
                    if num_articles in self.dict:
                        self.dict[num_articles] += 1
                    else:
                        self.dict[num_articles] = 1
                print("###################")
            except Exception as ex:
                print('A ' + str(ex) + ' error occured while web crawling.')
                print('This error occured on the article: ' + curr_article)
                continue

        per = 100 * float(final_count)/float(MAX_ITER)
        print("\nPercentage of pages often lead to philosophy -", round(per, 2), "%")

    def plot_histogram(self, filename):
        '''
        Creates a Histogram plot of the distribution obtained for different pages.
        '''
        sorted_keys = sorted(self.dict)
        sorted_dict = {}
        for key in sorted_keys:
            sorted_dict[key] = self.dict[key]
        X = np.arange(len(sorted_dict))
        plt.bar(X, sorted_dict.values(), align='center', width=0.5)
        plt.xticks(X, sorted_dict.keys())
        ymax = max(sorted_dict.values()) + 1
        plt.ylim(0, ymax)
        plt.xlabel('Path - Distance')
        plt.ylabel('Frequency')
        plt.savefig(filename)
        #plt.show()

#Initializes the wikipedia crawler
wiki_crawler = Wikipedia_Crawler()
wiki_crawler.find_philosophy()
wiki_crawler.plot_histogram(OUT_FILE)