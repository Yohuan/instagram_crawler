# -*- coding: utf8 -*-
import os
import sys
import util
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


OUTPUT_DIR = "./outputs"


class IgBrowser(object):
    """A simulated instagram browser.

    Use "selenium" to open the browser
    """
    igUrl = "https://www.instagram.com"
    sleepTime = 1
    # loadMorePostStr = "Load more"
    loadMorePostStr = "載入更多內容"
    # loadMoreCommentStr = "Load more comments"
    loadMoreCommentStr = "載入更多留言"

    def __init__(self, userName):
        self.driver = webdriver.Chrome()
        self.userName = userName
        self.goToProfilePage()

    def goToProfilePage(self):
        profileUrl = self.igUrl + '/' + self.userName
        self.driver.get(profileUrl)
        sleep(self.sleepTime)

    def scrollDown(self, numPost):
        """Scroll the page down.

        Until to show at least numPost posts
        """
        print("Scrolling down ...")
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(self.sleepTime)
        self.driver.find_element_by_link_text(self.loadMorePostStr).click()
        sleep(self.sleepTime)

        n = self.getNumPost()
        while n < numPost:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(self.sleepTime)
            n = self.getNumPost()
            util.debugPrint("%d posts" % n)
        sleep(5)

    def getUserInfo(self):
        print("Extracting %s's profile info ..." % self.userName)
        soup = BeautifulSoup(self.driver.page_source, features='lxml')
        spans = soup.find_all('span', {'class': '_fd86t'})

        if len(spans) != 3:
            sys.exit("Something wrong while getting user info !")

        return {"numPost": util.convert2Int(spans[0].get_text()),
                "numFollower": spans[1].get_text(),
                "numFollowing": spans[2].get_text()
                }

    def getPostInfo(self, postUrl):
        print("Extracting post info ...")
        self.driver.get(postUrl)
        sleep(self.sleepTime)

        try:
            while True:
                self.driver.find_element_by_link_text(self.loadMoreCommentStr).click()
                sleep(self.sleepTime)
        except NoSuchElementException:
            print("No more buttons")

        soup = BeautifulSoup(self.driver.page_source, features='lxml')

        like = soup.find('span', {'class': '_nzn1h'})
        numLike = util.convert2Int(like.span.get_text()) if like is not None else 0

        comments = self.getComments(soup)

        return {"numLike": numLike,
                "comments": comments}

    def getPostUrls(self):
        """Get the post urls shown in the current page.
        """
        print("Extracting %s's post URLs ..." % self.userName)
        soup = BeautifulSoup(self.driver.page_source, features='lxml')
        urls = soup.find_all('div', {'class': '_mck9w'})
        urls = [self.padUrl(url.a['href']) for url in urls]

        return urls

    def getNumPost(self):
        return len(self.driver.find_elements_by_class_name('_mck9w'))

    def output(self, outputDir, i, postInfo):
        print("Outputing %d th post ..." % i)
        os.makedirs(os.path.join(outputDir, self.userName, "%d_post" % i))
        fileName = os.path.join(outputDir, self.userName, "%d_post" % i, "comments.txt")
        with open(fileName, 'w') as f:
            f.write("%d likes\n" % postInfo["numLike"])
            for comment in postInfo["comments"]:
                f.write("%s\n" % comment)

    def close(self):
        self.driver.quit()

    @classmethod
    def padUrl(cls, url):
        """Complete the url.
        """
        return cls.igUrl + url

    @staticmethod
    def getComments(cls, soup):
        comments = soup.find_all('li', {'class': '_ezgzd'})
        comments = [comment.span.get_text() for comment in comments]
        return comments


if __name__ == '__main__':
    userNames = util.getUserNames()
    util.resetDir(OUTPUT_DIR)
    for userName in userNames:
        try:
            igBrowser = IgBrowser(userName)
            userInfo = igBrowser.getUserInfo()
            util.debugPrint("# Post: %d" % userInfo["numPost"])
            util.debugPrint("# Follower: %s" % userInfo["numFollower"])
            util.debugPrint("# Following: %s" % userInfo["numFollowing"])

            if userInfo["numPost"] > 12:
                igBrowser.scrollDown(userInfo["numPost"])

            postUrls = igBrowser.getPostUrls()
            assert len(postUrls) == userInfo["numPost"]

            for i, postUrl in enumerate(postUrls):
                print("%d th post" % (i + 1))
                postInfo = igBrowser.getPostInfo(postUrl)
                igBrowser.output(OUTPUT_DIR, i + 1, postInfo)

        except Exception as e:
            print(e)
        finally:
            igBrowser.close()
