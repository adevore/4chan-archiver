~~~~~~~~~~~~~~
4Chan Archiver
~~~~~~~~~~~~~~

:author: Aaron DeVore
:contact: aaron.devore@gmail.com

Archive images and post information from a 4chan thread.

------------
Dependencies
------------

* Python 3.1+
* BeautifulSoup 4.x
* Jinja2 (optional, for HTML output)
* Linux (not tested on Windows or Mac)

--------
Warning
--------

4chan has some nasty and/or illegal images. All images in a thread will
be downloaded! Images from ads are not downloaded. Author(s) shall not be
liable for any legal action result from use of this software. If you are
unsure if a thread will contain illegal images, use tmpfs. Keep that stuff
off your computer.

-------
Copying
-------

See LICENSE.txt.

---------
Archiving
---------

::

    ./archive.py [options] <board><thread> <destination>

board: Board (as in b)

thread: Thread ID

destination: Archive directory


Options
=======

  -h, --help            show this help message and exit
  -b BOARD, --board=BOARD
                        board name
  -o, --overwrite-images
                        Overwrite non-empty images
  -u, --update          update the thread
  -p PAUSEUPDATE, --pause-update=PAUSEUPDATE
                        Wait time between thread updates
  --pause-image=PAUSE_IMAGE
                        Wait time between image downloads

  -b <board> or --board <board>: Board to use (default: b)

  -o or --overwrite-images: Always download images instead of skipping already downloaded images

--------
Querying
--------

::

    ./query.py [options] <archive>

Options
=======

  -h, --help            show this help message and exit
  --author AUTHOR       Exact match author
  --author-re AUTHOR_RE Regexp match author
  --text TEXT           Exact match message body
  --text-re TEXT_RE     Regexp match message body
  --id ID, -i ID        Message id (repeatable)
  --ids IDS             Comma separated id list
  --images              Match only posts with images
  --no-images           Match only posts without images
  --green-text          Match only posts with green text
  --no-green-text       Match only posts without green text
  --out OUT, -o OUT     Output file
  --htmldir HTMLDIR     Write a full HTML directory including images
  --format FORMAT       Output format (html|json|plaintext)

Using --format html only outputs an HTML file. Use --htmldir to get a
directory with all files properly in place.

--------------
Archive Layout
--------------

::

    <destination>
    --<board>-<thread>/
    ----images/: Downloaded images
    ----thread.js: JSON file

-----------
JSON format
-----------

Format for board-thread/thread.js file::

    {
      "id": <thread ID>,
      "board": <board name>
      "mtime": <modified time using int(time.time())>
      "posts": [
          {
              "image": {
                  "original": The original name of the uploaded file
                  "name": File name of the image as written to disk
              }
              "utc": Time in seconds from the epoch
              "id": post ID,
              "text": Text of the post (raw HTML),
              "author": Author name (sometimes raw HTML)
          },
          ...
      ]
    }

