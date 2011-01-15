~~~~~~~~~~~~~~~~
4Chan Archiver
~~~~~~~~~~~~~~~~

:author: Aaron DeVore
:contact: aaron.devore@gmail.com

Archive images and post information from a 4chan thread.

------------
Dependencies
------------

* Python 2.6+
* BeautifulSoup 3.x

--------
Warning
--------

4chan has some nasty and/or illegal images. All images in a thread will
be downloaded! Images from ads are not downloaded. Author(s) shall not be
liable for any legal action result from use of this software.

-----
Usage
-----

::

    python archive.py [options] <thread> <destination>

thread: Thread ID

destination: Archive directory

-------
Options
-------

-b <board> or --board <board>: Board to use (default: b)

-o or --overwrite-images: Always download images instead of skipping already downloaded images

------
Layout
------

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
      "posts": [
          {
              "imageTitle": Original title of the image (null for no image),
              "image": New name of the image (null for no image)
              "timestamp": Timestamp taken straight from the page,
              "id": post ID,
              "text": Text of the post (raw HTML),
              "poster": Poster name (sometimes raw HTML)
          },
          ...
      ]
    }
