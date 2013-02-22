#!/usr/bin/env python3
# Copyright (c) 2010, Aaron DeVore
# Released under the Don't Be A Douchbag License.
# Use responsibly. Contribute changes if you feel like it. No CP!

import urllib.request, urllib.error
import os
import re
import time
from optparse import OptionParser
from bs4 import BeautifulSoup
import archivelib

# TODO: Switch to argparse
options = OptionParser()
options.add_option("-b", "--board", dest="board",
    default='mlp', help="board name")
options.add_option("-o", "--overwrite-images", dest="overwrite_images",
   default=False, help="Overwrite non-empty images", action="store_true")
options.add_option("-u", "--update", dest="update", action="store_true",
    default=False, help="update the thread")
options.add_option("-p", "--pause-update", type="int", dest="pauseUpdate",
    default=100, help="Wait time between thread updates")
options.add_option("--pause-image", type="int", dest="pause_image",
    default=1, help="Wait time between image downloads")


class Post(archivelib.Post):
    # Add image location attribute
    def __init__(self):
        self.image_location = None
        super().__init__()


def get_soup(thread):
    url = "http://boards.4chan.org/%s/res/%s" % (thread.board, thread.id)
    print("downloading thread %s for board %s at %s" %
          (thread.id, thread.board, url))
    f = urllib.request.urlopen(url)
    soup = BeautifulSoup(f)
    f.close()
    return soup


def parse_posts(soup, thread):
    image_count = 1  # OP has to have an image
    op = parse_post(soup.find(True, 'opContainer'))
    thread.add_post(op)

    for reply_container in soup.find_all(True, 'replyContainer'):
        reply = parse_post(reply_container)
        if reply.has_image:
            image_count += 1
        thread.add_post(reply)
 
    print("found {} posts with {} images".format(len(thread.posts),
                                                 image_count))


def parse_post(container):
    p = Post()
    # id, poster, subject
    p.id = int(container["id"][2:])
    p.author = container.find('span', 'name').text.strip()
    p.subject = container.find(True, 'subject').text.strip()

    post_number_tag = container.find('span', 'postNum')
    p.utc = int(post_number_tag["data-utc"])

    file_text_tag = container.find(True, 'fileText')
    if file_text_tag:
        location_tag = file_text_tag.a
        p.image_location = "http:" + location_tag["href"]
        p.image_name = location_tag.text.strip()
        p.image_original = file_text_tag.span.text.strip()

    post_message_tag = container.find('blockquote', 'postMessage')
    message = []
    for child in post_message_tag.descendants:
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


def write_data(thread, dest):
    target = os.path.join(dest, "thread.js")
    print("writing thread data for %s to %s" % (thread.id, target))
    with open(target, 'w') as f:
        thread.json_dump(f, indent=4)


def main():
    opts, args = options.parse_args()
    if len(args) != 2:
        print(options.usage)
    thread, baseDest = args

    thread_match = re.match("([a-z]+)(\d+)", thread)
    if not thread_match:
        print("Thread not of format <board><thread id>")
    thread = archivelib.Thread()
    thread.board = thread_match.group(1)
    thread.id = int(thread_match.group(2))

    overwrite_images = opts.overwrite_images
    if opts.update:
        updates = -1
    else:
        updates = 1
    dest = os.path.join(baseDest, "%s-%s" % (thread.board, thread.id))
    if not os.path.exists(dest):
        os.makedirs(dest)
    try:
        while updates != 0:
            updates -= 1
            soup = get_soup(thread)
            parse_posts(soup, thread)
            download_images(thread.posts, dest, overwrite_images,
                            opts.pause_image)

            write_data(thread, dest)

            if updates != 0:
                print("waiting %i seconds for next update" % opts.pauseUpdate)
                print("-" * 40)
                time.sleep(opts.pauseUpdate)
    except KeyboardInterrupt:
        print("Keyboard Interrupt, ending archiving")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Thread or image 404ed")
        else:
            raise

if __name__ == "__main__":
    main()
