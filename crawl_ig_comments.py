# -*- coding: utf8 -*-
from ig_browser import IgBrowser
import sys
import util

OUTPUT_DIR = "outputs"


def main():
    """Crawl post comments from specific users

    python crawl_ig_comments.py user1 user2 ...
    """
    userNames = util.getUserNames()
    util.resetDir(OUTPUT_DIR)
    for userName in userNames:
        try:
            igBrowser = IgBrowser(userName)
            userInfo = igBrowser.extractUserInfo()
            util.debugPrint("# Post: %d" % userInfo["numPost"])
            util.debugPrint("# Follower: %s" % userInfo["numFollower"])
            util.debugPrint("# Following: %s" % userInfo["numFollowing"])

            if userInfo["numPost"] > 12:
                postLimit = 100 if userInfo["numPost"] > 100 else userInfo["numPost"]
                igBrowser.scrollDown(postLimit)

            postUrls = igBrowser.extractPostUrls()

            for i, postUrl in enumerate(postUrls):
                print("%d th post" % (i + 1))
                postInfo = igBrowser.extractPostInfo(postUrl)
                igBrowser.output(OUTPUT_DIR, i + 1, postInfo)

        except Exception as e:
            print(e)

        finally:
            igBrowser.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(main.__doc__)
    main()
