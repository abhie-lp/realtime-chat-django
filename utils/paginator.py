"""Custom paginators"""

from django.core.paginator import Paginator
from django.core.cache import cache


# http://masnun.rocks/2017/03/20/django-admin-expensive-count-all-queries/
class CachingPaginator(Paginator):
    """Paginator for large number of rows"""

    def _get_count(self):
        if not hasattr(self, "_count"):
            self._count = None

        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(
                    self.object_list.query.__str__()
                ))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)
            except:
                self._count = len(self.object_list)
        return self._count
