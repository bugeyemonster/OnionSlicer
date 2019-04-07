"""
Things to do
1. Add time to calculate processing time and estimate time remaining
2. Command line args for host, proxyport, fileextension, wordlist, reverse yes or no, max threads
3. create a log file for each response code.
6. add more interesting request header information

"""

"""
Code by bugeyemonster
March 2019
version .01
this prorgam will attempt to find directories and files on a webserver
Specifically created for crawling via tor proxy for anonimity but also to crawl onion sites

"""
import time
import threading
import os
import urllib3
from urllib3.contrib.socks import SOCKSProxyManager

startTime = time.time()
targetUrl = "http://someonionsite.onion"
#targetUrl = "https://www.hackthissite.org"
proxy = SOCKSProxyManager('socks5h://127.0.0.1:9150/') # configured in tor browser or use tor docker

wordListFile = "directory-list-lowercase-2.3-medium.txt"
#wordListFile = "testlist.txt"

dirs = [] # dirs list will store target words
if wordListFile == "testlist.txt":
    hitLog = "os_hit_test.log"
    missLog = "os_miss_test.log"
else:
    hitLog = "os_hits.log"
    missLog = "os_miss.log"
# file extentions can be added to test for files
# this is not completely working yet
#fileExtenstion = "php"
fileExtenstion = False 

# function to write hits to a file
def log_hit(line):
    file = open(hitLog, 'a')
    file.write(line)
    file.close()

# function to write misses to a file
def log_miss(line):
    file = open(missLog, 'a')
    file.write(line)
    file.close()

# this is the function that tests the url
# this might be faster to do this with HEAD and then only do a GET if the page does not return a 404 or 400
def test_page(page):
    response = proxy.request('HEAD', page)
    if response.status != 404:
        response = proxy.request('GET', page)
        line = page + "\n" + str(response.status) + "\n" + str(response.headers) + "\n" + str(response.data) + "\n"
        log_hit(line)
    else:
        #line = page + " c0d3: " + str(response.status) + " h34d3r5: " + str(response.headers) + "\n"
        #log_miss(line) # this is really just for testing, no need to write out all the 404s
        pass
        #print(page + " c0d3: " + str(response.status) + " h34d3r5: " + str(response.headers) + "\n")
# function to build a List from a word list file for words to tests
# ToDO this function should strip out nonsense lines like comments at the top of word list.
def get_words(list):
    list = open(list,"r")
    for i in list.readlines():
        i = i.rstrip()
        if i.startswith("#"):
            continue
        else:
            dirs.append(i)

        #dirs.reverse() # reverse dir list, used to run a the script twice and process the list from oppisite directions
    list.close()

# function to build the url and pass it to the test_page function
def build_page_thread():
    testDir = dirs.pop()
    print("There are " + str(len(dirs)) + " elements left in dirs list")
    if "%EXT%" not in testDir:
        page = targetUrl + '/' + testDir.rstrip()
        t1 = threading.Thread(target=test_page, args=(page, )) # stage the thread
        page = targetUrl + '/' + testDir.rstrip() + '/'
        t2 = threading.Thread(target=test_page, args=(page, )) # stage the thread
        # kick off the two threads one with / one with out
        t1.start()
        time.sleep(.1)
        t2.start()
    elif fileExtenstion != False: # test what ever file extension is assigned
        testDir = testDir.rstrip()
        testDir = testDir.replace("%EXT%", fileExtenstion)
        page = targetUrl + '/' + testDir
        t = threading.Thread(target=test_page, args=(page, ))
        t.start()
    else:
        return # do nothing
get_words(wordListFile) # build the word list list
#print(dirs)
while len(dirs) > 0:
    threadCount = threading.active_count()
    print("thread count = " + str(threadCount))
    if threadCount < 50: # this number can likely be a lot higher
        if len(dirs) > 200: # this will create 400 threads the conditional could be changed to process faster
            for i in range(0, 200):
                build_page_thread()
        else:
            for i in range(0, len(dirs)): # this might need some more logic
                build_page_thread()
    else:
        time.sleep(1) # if a lot of threads are already running wait 1 second

while threading.active_count() > 1:
    time.sleep(1)

finTime = time.time()
totTime = (finTime - startTime) / 3600
print("Exectution time in hours: ", totTime)
