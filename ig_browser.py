# -*- coding: utf8 -*-
import os
import sys
import util
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from urllib.request import urlretrieve


class IgBrowser(object):
    """A simulated instagram browser.

    Use "selenium" to open the web page with Chrome
    """
    igUrl = "https://www.instagram.com"
    sleepTime = 1
    # loadMorePostStr = "Load more"
    # loadMoreCommentStr = "Load more comments"
    loadMorePostStr = "載入更多內容"
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

    def extractUserInfo(self):
        print("Extracting %s's profile info ..." % self.userName)
        soup = BeautifulSoup(self.driver.page_source, features='lxml')
        spans = soup.find_all('span', {'class': '_fd86t'})

        if len(spans) != 3:
            sys.exit("Something wrong while getting user info !")

        return {"numPost": util.convert2Int(spans[0].get_text()),
                "numFollower": spans[1].get_text(),
                "numFollowing": spans[2].get_text()
                }

    def extractPostInfo(self, postUrl):
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

        postType = "image" if self.isImage(soup) else "video"
        imgUrl = self.getImgUrl(soup, postType)

        like = soup.find('span', {'class': '_nzn1h'})
        numLike = util.convert2Int(like.span.get_text()) if like is not None else 0

        comments = self.getComments(soup)

        return {"type": postType,
                "imgUrl": imgUrl,
                "numLike": numLike,
                "comments": comments}

    def extractPostUrls(self):
        """Get the post urls shown in the current page.
        """
        print("Extracting %s's post URLs ..." % self.userName)
        soup = BeautifulSoup(self.driver.page_source, features='lxml')
        urls = soup.find_all('div', {'class': '_mck9w'})
        urls = [self.padUrl(url.a['href']) for url in urls]

        return urls

    def getNumPost(self):
        return len(self.driver.find_elements_by_class_name('_mck9w'))

    def output(self, outputDir, i, postInfo, includeImg=True):
        print("Outputing %d th post ..." % i)
        postDir = os.path.join(outputDir,
                               self.userName,
                               "%d_post_%s" % (i, postInfo["type"]))
        os.makedirs(postDir)
        fileName = os.path.join(postDir, "comments.txt")
        with open(fileName, 'w') as f:
            f.write("%d likes\n" % postInfo["numLike"])
            for comment in postInfo["comments"]:
                f.write("%s\n" % comment)

        imgName = "image.png" if postInfo["type"] == "image" else "video.png"
        imgName = os.path.join(postDir, imgName)
        if includeImg:
            urlretrieve(postInfo["imgUrl"], imgName)

    def close(self):
        self.driver.quit()

    @classmethod
    def padUrl(cls, url):
        """Complete the URL.
        """
        return cls.igUrl + url

    @staticmethod
    def getComments(soup):
        comments = soup.find_all('li', {'class': '_ezgzd'})
        comments = [comment.span.get_text() for comment in comments]
        return comments

    @staticmethod
    def isImage(soup):
        numView = soup.find_all('span', {'class': '_m5zti'})
        return True if not numView else False

    @staticmethod
    def getImgUrl(soup, postType):
        """
        If postType == video, then return a image representing that video
        """
        if postType == "image":
            try:
                img = soup.find('div', {'class': '_4rbun'})
                imgUrl = img.img['src']
            except Exception:
                imgUrl = None
        else:
            try:
                img = soup.find('div', {'class': '_qzesf'})
                imgUrl = img.video['poster']
            except Exception:
                imgUrl = None
        return imgUrl
