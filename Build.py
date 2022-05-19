import xml.etree.ElementTree as ElementTree
import shutil
import os
import warnings
from datetime import date


class Updates:
    def __init__(self, path):
        tree = ElementTree.parse( path )
        self.dates = list( map(lambda e: date.fromisoformat(e.text.strip()), tree.findall(".//*[@class='date']")) )
        self.descriptions = list( map(lambda e: e.text, tree.findall(".//*[@class='description']")) )

    update_item_string = """
        <div class="update-log-item">
            <span class="date">
            {}
            </span>
            <span class="description">
            {}
            </span>
        </div>
    """
    def get_update_item_string(self, index):
        return self.update_item_string.format(self.dates[index], self.descriptions[index])

    update_logs_string = """
    <div id="update-logs" class="collapsable collapsed">
        {}
        <div class="collapsable-body">
            {}
        </div>
    </div>
    """
    def get_update_logs_string(self):
        items = list( map(lambda i: self.get_update_item_string(i), range(len(self.dates))) )
        last = items.pop(0).replace("update-log-item", "update-log-item collapsable-title")
        rest = "\n".join(items)
        return self.update_logs_string.format(last, rest)

    def get_last_update_date(self):
        return self.dates[0]

    def get_last_update_string(self):
        return self.get_update_item_string(0).replace("update-log-item", "last-update")

class Tags:

    defined_tags = []

    def __init__(self, path):
        with open(path) as f:
            self.tags = set(f.readlines())

    tag_item_string = """
        <span class="{}">
        {}
        </span>
    """
    tags_string = """
        <div class="related-tags">
            {}
        </div>
    """
    def get_tags_string(self):
        content = "\n".join( map(lambda t: self.tag_item_string.format("related-tag-item", t), self.tags) )
        return self.tags_string.format(content)

    def is_valid(self):
        return self.tags <= self.defined_tags

    @classmethod
    def set_defined_tags(cls, path):
        with open(path) as f:
            cls.defined_tags = set(f.readlines())

    tag_filters_string = """
        <div id="tag-filters">
            <div id="tag-filter-title">
                Tag filter
            </div>
            {}
        </div>
    """
    @classmethod
    def get_filters_string(cls):
        content = "\n".join( map(lambda t: cls.tag_item_string.format("tag-filter-item", t), cls.defined_tags) )
        return cls.tag_filters_string.format(content)


class Article:

    def __init__(self, build_data):
        datas = build_data.split()
        self.last_built = date.fromisoformat(datas[0]) #YYYY-MM-DD
        self.directory = datas[1]
        path = os.path.join(self.directory, "article.html")
        with open(path) as f:
            self.title = f.readline().strip()
            self.main = "".join( f.readlines() )
        self.updates = Updates( os.path.join(self.directory, "updates.xml") )
        self.last_update = self.updates.get_last_update_date()
        self.tags = Tags( os.path.join(self.directory, "tags.txt") )
        if not(self.tags.is_valid()):
            warnings.warn("invalid tag :" + self.directory)

    def build(self, dest):
        page_string = ""
        with open(os.path.join("__Template", "Article.html")) as f:
            page_string = "".join(f.readlines())
        with open(os.path.join("__Template", "License.txt")) as f:
            license = "<br />".join(f.readlines()).replace("YEAR", str(self.last_update.year), 1)
        injection = {\
            "header_links": ArticleBuilder.header_footer_string.format("header-links") ,\
            "footer_links": ArticleBuilder.header_footer_string.format("footer-links") ,\
            "title": self.title ,\
            "update_logs": self.updates.get_update_logs_string() ,\
            "related_tags": self.tags.get_tags_string() ,\
            "section_main": self.main ,\
            "license": license \
        }
        page_string = ArticleBuilder.page_injection(page_string, injection)
        # write to file
        if not(os.access( os.path.join(dest, self.directory), os.F_OK )):
            os.mkdir(os.path.join(dest, self.directory))
        with open(os.path.join(dest, self.directory, "index.html"), "w") as f:
            f.write(page_string)
        #copy resources
        path = os.path.join(dest, self.directory, "resources")
        if os.path.exists(path):
            shutil.rmtree(path)
        shutil.copytree(os.path.join(self.directory, "resources"), path)
        self.last_built = self.last_update

    def get_build_log(self):
        return self.last_built.isoformat() + " " + self.directory

    link_string = """
        <a href="{}" class="article-item">
            <div class="article-title">
            {}
            </div>
            {}
            {}
        </a>
    """
    def get_link_string(self):
        return self.link_string.format(\
            (self.directory + "/index.html"),\
            self.title,\
            self.updates.get_last_update_string(),\
            self.tags.get_tags_string() \
            )


class ArticleBuilder:

    article_list_path = "ArticleList.txt"
    def __init__(self, dest):
        self.dest = dest
        self.articles = []

    header_footer_string = """
        <div id="{}">
            <a href="/" class="logo">UncoTechHack</a>
            <a href="/" class="top">TOP</a>
            <a href="/contents.html" class="contents">CONTENTS</a>
        </div>
    """

    @classmethod
    def page_injection(cls, page_string, dictionary):
        for k, v in dictionary.items():
            target = "<!--replace {}-->".format(k)
            page_string = page_string.replace(target, v)
        return page_string

    articles_string = """
        <div id="articles">
        {}
        </div>
    """
    def get_article_links_string(self):
        return self.articles_string.format("\n".join( map(lambda a: a.get_link_string(), self.articles) ))

    def build_contents_page(self):
        page_string = ""
        with open(os.path.join("__Template", "Contents.html")) as f:
            page_string = "".join(f.readlines())
        injection = {\
            "header_links": ArticleBuilder.header_footer_string.format("header-links") ,\
            "footer_links": ArticleBuilder.header_footer_string.format("footer-links") ,\
            "tag_filters": Tags.get_filters_string() ,\
            "article_links": self.get_article_links_string() \
        }
        page_string = ArticleBuilder.page_injection(page_string, injection)
        with open(os.path.join(self.dest, "contents.html"), "w") as f:
            f.write(page_string)

    def build(self):
        Tags.set_defined_tags("TagList.txt")
        with open(self.article_list_path) as f:
            self.articles = list( map(lambda l: Article(l), f.readlines()) )
        for a in self.articles:
            if a.last_built < a.last_update:
                a.build(self.dest)
        self.articles.sort(key = lambda a: a.last_built, reverse = True)
        self.build_contents_page()
        with open(self.article_list_path, "w") as f:
            f.write("\n".join( map(lambda a: a.get_build_log(), self.articles) ))


if __name__ == "__main__":
    import sys
    dest_dir = os.path.join("..", "publish")
    builder = ArticleBuilder( dest_dir )
    builder.build()
