import re

re_slug = re.compile(r'[^A-Za-z0-9_]+')

def slug(s):
    return re_slug.sub('-', s)
