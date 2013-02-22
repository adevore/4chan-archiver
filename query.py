#!/usr/bin/env python3
# query

import argparse
from functools import partial
import os
import sys
import re
import shutil

import archivelib


DESCRIPTION = "Query 4chan Archiver archives"


arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
arg_parser.add_argument('--author', help="Exact match author")
arg_parser.add_argument('--author-re', help="Regexp match author")
arg_parser.add_argument('--text', help="Exact match message body")
arg_parser.add_argument('--text-re', help="Regexp match message body")
arg_parser.add_argument('--id', '-i', type=int, action="append",
                        help="Message id (repeatable)")
arg_parser.add_argument('--ids', help="Comma separated id list")
arg_parser.add_argument('--images', action="store_true",
                        help="Match only posts with images")
arg_parser.add_argument('--no-images', action="store_false",
                        help="Match only posts without images")
arg_parser.add_argument('--green-text', action="store_true",
                        help="Match only posts with greentext")
arg_parser.add_argument('--no-green-text', action="store_false",
                        help="Match only posts without greentext")
arg_parser.add_argument('--out', '-o', help="Output file")
arg_parser.add_argument('--htmldir',
                        help="Write a full HTML directory inc. images")
arg_parser.add_argument('--format', default="json",
                        help="Output format (html|json|plaintext)")
arg_parser.add_argument('path', help="Thread archive location")


def constraint_regexp(attr, regexp, post):
    return bool(regexp.match(getattr(post, attr)))


def constraint_equal(attr, value, post):
    return getattr(post, attr) == value


def constraint_contains(attr, values, post):
    return getattr(post, attr) in values


def make_constraints(opts):
    constraints = []
    if opts.author:
        constraints.append(partial(constraint_equal, "author",
                           opts.author))
    elif opts.author_re:
        constraints.append(partial(constraint_regexp, "author",
                           re.compile(opts.author_re, re.I)))

    if opts.text:
        constraints.append(partial(constraint_equal, "text",
                           opts.text))
    elif opts.text_re:
        constraints.append(partial(constraint_regexp, "text",
                           re.compile(opts.text_re, re.I)))

    ids = []
    if opts.ids:
        ids.extend(map(int, ids))
    if opts.id:
        ids.extend(opts.id)

    if ids:
        constraints.append( partial(constraint_contains, "id", ids))
        
    if opts.images:
        constraints.append(partial(constraint_equal, "has_image", True))
        
    if opts.no_images is False:
        constraints.append(partial(constraint_equal, "has_image", False))
        
    if opts.green_text:
        constraints.append(partial(constraint_equal, "has_greentext", True))
        
    if opts.no_green_text is False:
        constraints.append(partial(constraint_equal, "has_greentext", False))

    return constraints


def filter_posts(thread, constraints):
    return [post for post in thread.posts
            if all(constraint(post) for constraint in constraints)]


def output(f, format, thread, posts):
    if format == "json":
        thread.json_dump(f, subset=posts, indent=4)
    elif format == "html":
        f.write(archivelib.render_html(thread, posts))
    elif format == "plaintext":
        f.write(archivelib.render_plaintext(thread, posts))
        
        
def write_html_dir(src, dest, thread, posts):
    image_src_dir = os.path.join(src, "images")
    image_dest_dir = os.path.join(dest, "images")
    html_dest = os.path.join(dest, "thread.html")
    os.makedirs(dest, exist_ok=True)
    shutil.copytree(image_src_dir, image_dest_dir)
    with open(html_dest, "w") as f:
        f.write(archivelib.render_html(thread, posts))


def main():
    opts = arg_parser.parse_args()
    constraints = make_constraints(opts)
    thread = archivelib.Thread(os.path.expanduser(opts.path))
    posts = filter_posts(thread, constraints)
    if opts.htmldir:
        write_html_dir(os.path.expanduser(opts.path),
                       os.path.expanduser(opts.htmldir),
                       thread, posts)
    elif opts.out:
        with open(opts.out, "w") as f:
            output(f, opts.format, thread, posts)
    else:
        output(sys.stdout, opts.format, thread, posts)
 
if __name__ == '__main__':
    main()