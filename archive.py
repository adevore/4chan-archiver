<<<<<<< HEAD
#!/usr/bin/env python3
=======
#!/usr/bin/env python
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
# Copyright (c) 2010, Aaron DeVore
# Released under the Don't Be A Douchbag License.
# Use responsibly. Contribute changes if you feel like it. No CP!

<<<<<<< HEAD


import urllib.request, urllib.error
=======
import urllib2
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
import os
import posixpath
import json
import time
from optparse import OptionParser
<<<<<<< HEAD
from bs4 import BeautifulSoup

options = OptionParser()
options.add_option("-b", "--board", dest="board",
    default='mlp', help="board name")
options.add_option("-o", "--overwrite-images", dest="overwrite_images",
=======
from BeautifulSoup import BeautifulSoup, Tag
import htmlentitydefs

USAGE = "%prog [options] <thread ID> <base directory>"

options = OptionParser(usage=USAGE)
options.add_option("-b", "--board", dest="board",
    default='b', help="board name")
options.add_option("-o", "--overwrite-images", dest="overwriteImages",
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
    default=False, help="Overwrite non-empty images", action="store_true")
options.add_option("-u", "--update", dest="update", action="store_true",
    default=False, help="update the thread")
options.add_option("-p", "--pause-update", type="int", dest="pauseUpdate",
    default=100, help="Wait time between thread updates")
<<<<<<< HEAD
options.add_option("--pause-image", type="int", dest="pause_image",
    default=1, help="Wait time between image downloads")


class Post(object):
    def __init__(self):
        self.image_name = self.image_location = self.image_original = None

    @property
    def has_image(self):
        return self.image_name is not None

    def __repr__(self):
        if self.image_name:
            return "%(id)s by %(poster)s with %(image)s" % self.__dict__
        else:
            return "{id} by {poster} with no {image}".format(self.__dict__)


def get_soup(board, thread):
    url = "http://boards.4chan.org/%s/res/%s" % (board, thread)
    print("downloading thread %s for board %s at %s" % (thread, board, url))
    f = urllib.request.urlopen(url)
=======
options.add_option("--pause-image", type="int", dest="pauseImage",
    default=1, help="Wait time between image downloads")
options.add_option("-n", "--no-pics", action="store_false", dest="pics", default=True,
    help="Do not download pictures")


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
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
    soup = BeautifulSoup(f)
    f.close()
    return soup

<<<<<<< HEAD

def parse_posts(soup):
    image_count = 1  # OP has to have an image
    op = parse_post(soup.find(True, 'opContainer'))
    posts = [op]

    for reply_container in soup.find_all(True, 'replyContainer'):
        reply = parse_post(reply_container)
        if reply.image_name:
            image_count += 1
        posts.append(reply)
        
    print("found {} posts with {} images".format(len(posts), image_count))
    return posts


def parse_post(container):
    p = Post()
    # id, poster, subject
    p.id = int(container["id"][2:])
    p.poster = container.find('span', 'name').text.strip()
    p.subject = container.find(True, 'subject').text.strip()

    post_number_tag = container.find('span', 'postNum')
    p.utc = post_number_tag["data-utc"]
    p.timestamp = post_number_tag.text.strip()

    file_text_tag = container.find(True, 'fileText')
    if file_text_tag:
        location_tag = file_text_tag.a
        p.image_location = "http:" + location_tag["href"]
        p.image_name = location_tag.text.strip()
        p.image_original = file_text_tag.span.text.strip()

    post_message_tag = container.find('blockquote', 'postMessage')
    message = []
    for child in post_message_tag.children:
        if isinstance(child, str):
            message.append(child)
        elif child.name == 'br':
            message.append('\n')
    p.text = ''.join(message)

    return p
    

def download_images(posts, dest, overwrite_images, pause_image):
    image_dir = os.path.join(dest, "images")
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)
    print("pause time between image requests:", pause_image)
    for post in posts:
        if post.has_image:
            local_path = os.path.join(image_dir, post.image_name)
            if os.path.exists(local_path):
                if not overwrite_images and os.path.getsize(local_path) != 0:
                    print("Skip: image %s already exists" % post.image_name)
                    continue
            print("downloading %s to %s" % (post.image_location, post.image_name))
            with open(local_path, 'wb') as f:
                try:
                    remote = urllib.request.urlopen(post.image_location)
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        print("image 404ed")
                    raise
                f.write(remote.read())
            time.sleep(pause_image) # be nice to the servers


def write_data(thread, posts, dest):
=======
def getText(tag, seperator=u""):
    """
    Get all child text for a tag.
    """
    text = []
    for node in tag.recursiveChildGenerator():
        if isinstance(node, Tag) and node.name == "br":
            text.append(u"\n")
            continue
        elif not isinstance(node, unicode):
            continue
        for find, replace in htmlentitydefs.name2codepoint.items():
            node = node.replace(u"&%s;" % find, unichr(replace))
        text.append(node)
    return seperator.join(text)
            
        
def getOP(soup):
    threadNode = soup.find("form", {'name': "delform"})
    timestamp = threadNode.find("span", 'posttime').string
    poster = threadNode.find("span", "postername").string
    imageNode = threadNode.find("span", "filesize")
    imageURL = imageNode.a["href"]
    imageTitle = imageNode.findNext("span", "filetitle").string
    postID = threadNode.find("input", type="checkbox", value="delete")["name"]
    text = getText(threadNode.blockquote, " ")
    return Post(postID, text, poster, timestamp, imageURL, imageTitle)


def getRegularPosts(soup, posts):
    postTables = (td.findParent('table')
        for td in soup.findAll('td', 'doubledash'))
    imageCount = 0

    for postTable in postTables:
        postID = postTable.find('td', id=True)['id']
        text = getText(postTable.find('blockquote'), u" ")
        posterSpan = postTable.find('span', 'commentpostername')
        poster = posterSpan.string
        timestamp = posterSpan.findNextSibling(text=True)

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
    return imageCount

def getPosts(soup):
    posts = [getOP(soup)]
    imageCount = 1 # Start at 1 for OP's image
    imageCount += getRegularPosts(soup, posts)
    print u"found %i posts with %i images" % (len(posts), imageCount)
    return posts


def downloadImages(posts, dest, overwriteImages, pauseImage):
    imageDir = os.path.join(dest, "images")
    if not os.path.exists(imageDir):
        os.mkdir(imageDir)
    print "pause time between image requests:", pauseImage
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
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
    target = os.path.join(dest, "thread.js")
    jsonPosts = []
    jsonCode = {}
    jsonCode['id'] = thread
<<<<<<< HEAD
=======

>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
    jsonCode['posts'] = jsonPosts
    for post in posts:
        jsonPosts.append({
            'id': post.id,
            'poster': post.poster,
<<<<<<< HEAD
            'subject': post.subject,
            'image': {
                    'name': post.image_name,
                    'original': post.image_original,
                    },
            'timestamp': post.timestamp,
            'utc': post.utc,
            'text': post.text,
            })
    print("writing thread data for %s to %s" % (thread, target))
    with open(target, 'w') as f:
        json.dump(jsonCode, f)
=======
            'image': post.image,
            'timestamp': post.timestamp,
            'text': post.text,
            'imageTitle': post.imageTitle,
            })
    print u"writing thread data for %s to %s" % (thread, target)
    with open(target, 'w') as f:
        json.dump(jsonCode, f, indent=4)
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376


def main():
    opts, args = options.parse_args()
    if len(args) != 2:
<<<<<<< HEAD
        print(options.usage)
    thread = args[0]
    baseDest = args[1]
    board = opts.board
    overwrite_images = opts.overwrite_images
=======
        options.print_usage()
    thread = args[0]
    baseDest = args[1]
    board = opts.board
    overwriteImages = opts.overwriteImages
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
    if opts.update:
        updates = -1
    else:
        updates = 1
<<<<<<< HEAD
    dest = os.path.join(baseDest, "%s-%s" % (board, thread))
=======
    dest = os.path.join(baseDest, u"%s-%s" % (board, thread))
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
    if not os.path.exists(dest):
        os.makedirs(dest)
    try:
        while updates != 0:
            updates -= 1
<<<<<<< HEAD
            soup = get_soup(opts.board, thread)
            posts = parse_posts(soup)
            download_images(posts, dest, overwrite_images, opts.pause_image)
            write_data(thread, posts, dest)
            if updates != 0:
                print("waiting %i seconds for next update" % opts.pauseUpdate)
                print("-" * 40)
                time.sleep(opts.pauseUpdate)
    except KeyboardInterrupt:
        print("Keyboard Interrupt, ending archiving")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Thread or image 404ed")
=======
            soup = getSoup(opts.board, thread)
            posts = getPosts(soup)
            if opts.pics:
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
>>>>>>> 7e754367f44d8a6764ec9062fce027520702b376
        else:
            raise

if __name__ == "__main__":
    main()
