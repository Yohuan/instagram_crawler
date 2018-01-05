# -*- coding: utf8 -*-
import os
import sys
import shutil
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


INSTAGRAM_URL = "https://www.instagram.com"
OUTPUT_DIR = "./outputs"

def debugPrint(*args, **kwargs):
    if __debug__:
        print(*args, **kwargs)


def convert2Int(string):
    return int(string.replace(',', ''))


def getUserNames():
    if len(sys.argv) < 2:
        sys.exit("Please provide at least one username!\n")
    return sys.argv[1:]


def getUserInfo(driver, profileUrl):
    print("Extracting user info ...")
    driver.get(profileUrl)
    sleep(1)
    soup = BeautifulSoup(driver.page_source, features='lxml')
    spans = soup.find_all('span', {'class': '_fd86t'})

    if len(spans) != 3:
        sys.exit("Something wrong while getting user info !")

    return {"numPost": convert2Int(spans[0].get_text()),
            "numFollower": spans[1].get_text(),
            "numFollowing": spans[2].get_text()
            }


def collectComments(soup):
    comments = soup.find_all('li', {'class': '_ezgzd'})
    comments = [comment.span.get_text() for comment in comments]
    return comments


def getPostInfo(driver, postUrl, sleepTime=1):
    print("Extracting post info ...")
    driver.get(postUrl)
    sleep(1)

    try:
        while True:
            driver.find_element_by_link_text('Load more comments').click()
            sleep(sleepTime)
    except NoSuchElementException as error:
        print("No more buttons")

    soup = BeautifulSoup(driver.page_source, features='lxml')

    like = soup.find('span', {'class': '_nzn1h'})
    numLike = convert2Int(like.span.get_text()) if like is not None else 0

    comments = collectComments(soup)

    return {"numLike": numLike,
            "comments": comments}


def scrollDown(driver, numTotalPost, sleepTime=1):
    """Scroll the page down.

    To show all the posts
    """
    print("Scrolling down ...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(sleepTime)
    driver.find_element_by_link_text('Load more').click()
    sleep(sleepTime)

    numPost = len(driver.find_elements_by_class_name('_mck9w'))
    while numPost < numTotalPost:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(sleepTime)
        numPost = len(driver.find_elements_by_class_name('_mck9w'))
        debugPrint(numPost)
    sleep(5)


def padUrl(url):
    """Complete the url.
    """
    return INSTAGRAM_URL + url


def getPostUrls(driver, profileUrl):
    """Get all the post urls from profile page.
    """
    print("Getting user's post URLs ...")
    soup = BeautifulSoup(driver.page_source, features='lxml')
    urls = soup.find_all('div', {'class': '_mck9w'})
    urls = [padUrl(url.a['href']) for url in urls]

    return urls


def output(userName, i, postInfo):
    print("Outputing %d th post ..." % i)
    os.makedirs(os.path.join(OUTPUT_DIR, userName, "%d_post" % i))
    fileName = os.path.join(OUTPUT_DIR, userName, "%d_post" % i, "comments.txt")
    with open(fileName, 'w') as f:
        f.write("%d likes\n" % postInfo["numLike"])
        for comment in postInfo["comments"]:
            f.write("%s\n" % comment)
    print(postInfo["numLike"])
    print(postInfo["comments"])


def resetDir(path):
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)


if __name__ == '__main__':
    userNames = getUserNames()
    driver = webdriver.Chrome()
    resetDir(OUTPUT_DIR)
    for userName in userNames:
        profileUrl = INSTAGRAM_URL + '/' + userName
        userInfo = getUserInfo(driver, profileUrl)
        print("# Post: %d" % userInfo["numPost"])
        print("# Follower: %s" % userInfo["numFollower"])
        print("# Following: %s" % userInfo["numFollowing"])

        if userInfo["numPost"] > 12:
            scrollDown(driver, userInfo["numPost"])

        postUrls = getPostUrls(driver, profileUrl)
        print(len(postUrls))
        for i, postUrl in enumerate(postUrls):
            print("%d th post" % (i + 1))
            postInfo = getPostInfo(driver, postUrl, sleepTime=3)
            output(userName, i + 1, postInfo)

        driver.quit()
