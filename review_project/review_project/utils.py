def make_clickable_link(object, title = None, options = ''):
    try :
        if title is None:
            title = str(object)
        return "<a {} href='{}'>{}</a>".format(options, object.get_absolute_url(), title)
    except AttributeError:
        return ""

def wrap_album_popover(string, html_class, mbid):
    return "<album_popover mbid='{}' class='{}'>".format(mbid, html_class) + string + "</album_popover>"


def make_popover_link(object, title=None):
    return wrap_album_popover(make_clickable_link(object, title=title, options="slot='preview'"), "d-inline", object.mbid)
