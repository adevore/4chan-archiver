#!/usr/bin/env python
# Copyright (c) 2010, Aaron DeVore
# Released under the Don't Be A Douchbag License.
# Use responsibly. Contribute changes if you feel like it. No CP!

import urllib2
import os
import posixpath
import json
import time
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup

options = OptionParser()
options.add_option("-b", "--board", dest="board",
    default='b', help="board name")
options.add_option("-o", "--overwrite-images", dest="overwriteImages",
    default=False, help="Overwrite non-empty images", action="store_true")
options.add_option("-u", "--update", dest="update", action="store_true",
    default=False, help="update the thread")
options.add_option("-p", "--pause-update", type="int", dest="pauseUpdate",
    default=10, help="Wait time between thread updates")
options.add_option("--pause-image", type="int", dest="pauseImage",
    default=1, help="Wait time between image downloads")


class Post(object):
    def __init__(self, postID, text, poster, timestamp, image, imageTitle):
        self.id = postID
        self.text = text
        self.poster = poster
        self.timestamp = timestamp
        if image:
            self.image = posixpath.basename(image)
            self.imageURL = image
            self.imageTitle = imageTitle
        else:
            self.imageURL = self.image = self.imageTitle = None
    def __repr__(self):
        if self.image:
            return u"%(id)s by %(poster)s with %(image)s" % self.__dict__
        else:
            return u"%(id)s by %(poster)s with no image" % self.__dict__


def getSoup(board, thread):
    url = "http://boards.4chan.org/%s/res/%s" % (board, thread)
    print "downloading thread %s for board %s at %s" % (thread, board, url)
    f = urllib2.urlopen(url)
    soup = BeautifulSoup(f)
    f.close()
    return soup


def getPosts(soup):
    posts = []
    imageCount = 0
    postTables = (td.findParent('table')
        for td in soup.findAll('td', 'doubledash'))

    for postTable in postTables:
        postID = postTable.find('td', id=True)['id']
        text = postTable.find('blockquote').renderContents().strip()
        posterSpan = postTable.find('span', 'commentpostername')
        poster = posterSpan.string
        timestamp = posterSpan.findNext(text=True)

        filespan = postTable.find('span', 'filesize')
        if filespan:
            imageCount += 1
            imageURL = filespan.find('a')['href']
            imageTitle = postTable.find('span', title=True).string
        else:
            imageURL = None
            imageTitle = None

        post = Post(postID, text, poster, timestamp, imageURL, imageTitle)
        print u"found %s" % post
        posts.append(post)
    print u"found %i posts with %i images" % (len(posts), imageCount)
    return posts


def downloadImages(posts, dest, overwriteImages, pauseImage):
    imageDir = os.path.join(dest, "images")
    if not os.path.exists(imageDir):
        os.mkdir(imageDir)
    print "pause time between requests:", pauseImage
    for post in posts:
        if post.image:
            localPath = os.path.join(imageDir, post.image)
            if os.path.exists(localPath):
                if not overwriteImages and os.path.getsize(localPath) != 0:
                    print u"Skip: image %s already exists" % post.image
                    continue
            print u"downloading %s to %s" % (post.imageURL, post.image)
            with open(localPath, 'w') as f:
                try:
                    remote = urllib2.urlopen(post.imageURL)
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        print "image 404ed"
                    raise
                f.write(remote.read())
            time.sleep(pauseImage) # be nice to the servers


def writeData(thread, posts, dest):
    target = os.path.join(dest, "thread.js")
    jsonPosts = []
    jsonCode = {}
    jsonCode['id'] = thread
    jsonCode['posts'] = jsonPosts
    for post in posts:
        jsonPosts.append({
            'id': post.id,
            'poster': post.poster,
            'image': post.image,
            'timestamp': post.timestamp,
            'text': post.text,
            'imageTitle': post.imageTitle,
            })
    print u"writing thread data for %s to %s" % (thread, target)
    with open(target, 'w') as f:
        json.dump(jsonCode, f)


def main():
    opts, args = options.parse_args()
    if len(args) != 2:
        print options.usage
    thread = args[0]
    baseDest = args[1]
    board = opts.board
    overwriteImages = opts.overwriteImages
    if opts.update:
        updates = -1
    else:
        updates = 1
    dest = os.path.join(baseDest, u"%s-%s" % (board, thread))
    if not os.path.exists(dest):
        os.makedirs(dest)
    try:
        while updates != 0:
            updates -= 1
            soup = getSoup(opts.board, thread)
            posts = getPosts(soup)
            downloadImages(posts, dest, overwriteImages, opts.pauseImage)
            writeData(thread, posts, dest)
            if updates != 0:
                print "waiting %i seconds for next update" % opts.pauseUpdate
                print "-" * 40
                time.sleep(opts.pauseUpdate)
    except KeyboardInterrupt:
        print "Keyboard Interrupt, ending archiving"
    except urllib2.HTTPError, e:
        if e.code == 404:
            print "Thread or image 404ed"
        else:
            raise

if __name__ == "__main__":
    main()