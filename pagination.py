from math import ceil
from flask import request, url_for


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        if page < 1:
            page = 1
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_page(self):
        if self.page > 2:
            if self.page > self.pages:
                self.page = self.pages + 1
            return url_for(request.endpoint, p=self.page - 1)
        else:
            return url_for(request.endpoint)

    @property
    def next_page(self):
        return url_for(request.endpoint, p=self.page + 1)
