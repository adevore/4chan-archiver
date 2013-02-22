import json
import os
import textwrap
import io
import time

try:
    import jinja2
except ImportError:
    jinja2 = None
    
EMPTY_SUBJECT = "No Subject"


class Thread:
    """
    """
    def __init__(self, archive_path=None):
        self.archive_path = archive_path
        if archive_path:
            with open(os.path.join(archive_path, "thread.js")) as f:
                json_code = json.load(f)
            self.id = json_code['id']
            self.posts = list(map(Post, json_code['posts']))
            self.board = json_code['board']
        else:
            self.id = 0
            self.posts = []
            self.board = ""
        
    def json_dump(self, f, subset=None, **kwargs):
        json_code = {}
        json_code['id'] = self.id
        json_code['mtime'] = int(time.time())
        json_code['board'] = self.board
        if subset is None:
            subset = self.posts
        json_code['posts'] = [post.dict for post in subset]
        json.dump(json_code, f, **kwargs)
 
    def json_dumps(self, subset=None, **kwargs):
        bytesio = io.BytesIO()
        self.json_dumps(bytesio, subset, **kwargs)
        return bytesio.getvalue()
    
    def add_post(self, post):
        self.posts.append(post)
        
    def copy(self):
        new = Thread()
        new.id = self.id
        new.board = self.board
        new.posts = [post.copy() for post in self.posts]


class Post:
    def __init__(self, json_code=None):
        if json_code:
            js = json_code
            self.id = js['id']
            self.author = js['author']
            self.subject = js['subject']
            self.text = js['text']
            if 'image' in js:
                self.image_name = js['image']['name']
                self.image_original = js['image']['original']
            else:
                self.image_name = self.image_original = None
            self.utc = js['utc']
        else:
            self.id = 0
            self.poster = ""
            self.subject = ""
            self.text = ""
            self.image_name = None
            self.image_original = None
            self.utc = 0
 
    @property
    def timestamp(self):
        return time.strftime("%m/%d/%y(%a)%H:%M", time.gmtime(self.utc))

    @property
    def dict(self):
        d = {
            'id': self.id,
            'utc': self.utc,
            "text": self.text,
            'subject': self.subject,
            'author': self.author,
            }
        if self.has_image:
            d['image'] = {
                'name': self.image_name,
                'original': self.image_original
            }
        return d

    @property
    def paragraphs(self):
        return [Paragraph(p) for p in self.text.split("\n")]
    
    @paragraphs.setter
    def paragraphs(self, ps):
        self.text = "\n".join(ps)
        
    @property
    def subject_defaulting(self):
        if not self.subject:
            return EMPTY_SUBJECT
        else:
            return self.subject
        
    @property
    def has_image(self):
        return self.image_name is not None
        
    @property
    def has_greentext(self):
        return any(p.startswith(">") for p in self.paragraphs)
        
    def __repr__(self):
        if self.image_name:
            return "%(id)s by %(poster)s with %(image)s" % self.__dict__
        else:
            return "{id} by {poster} with no {image}".format(**self.__dict__)


class Paragraph(str):
    @property
    def is_quote(self):
        return self.startswith(">")
    
    def to_tag(self, soup, green_text_class="quote"):
        """
        Make a Beautiful Soup <p> tag
        """
        p_tag = soup.new_tag('p')
        if self.startswith('>'):
            span_tag = soup.new_tag("span")
            span_tag["class"] = green_text_class
            span_tag.string = self
            p_tag.append(span_tag)
        else:
            p_tag.string = self
        return p_tag
    
    def __repr__(self):
        return "Paragraph(%s)" % self


def render_template(thread, template_name, posts=None):
    if posts is None:
        posts = thread.posts
    if jinja2 is None:
        raise NotImplemented("Jinja2 not installed")

    loader = jinja2.FileSystemLoader("templates")
    env = jinja2.Environment(loader=loader)
    
    template = env.get_template(template_name)
    return template.render(thread=thread, posts=posts, textwrap=textwrap)


def render_html(thread, posts=None):
    return render_template(thread, "thread.html", posts)


def render_plaintext(thread, posts=None):
    if posts is None:
        post = thread.posts
    lines = []

    def write(*text):
        lines.append("".join(text))

    write("Thread: {thread.id} on /{thread.board}/".format(
                thread=thread))
    write()
    for post in posts:
        write("Subject: " + post.subject_defaulting)
        write("Author: " + post.author)
        write("Time: " + post.timestamp)
        if post.has_image:
            write("Image Original: " + post.image_original)
            write("Image Name: " + post.image_name)
        write()
        for paragraph in post.paragraphs:
            if paragraph != "":
                write(textwrap.fill(paragraph))
                write()
        write("=" *  70)
    # Remove the last separator iff there was a post found
    if lines[-1] == "=" * 70:
        del lines[-1]
    
    return "\n".join(lines)