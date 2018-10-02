def make_clickable_link(object, title = None):
    try :
        if title is None:
            title = str(object)
        return "<a href='{}'>{}</a>".format(object.get_absolute_url(), title)
    except AttributeError:
        return ""
