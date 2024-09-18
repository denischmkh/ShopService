from dataclasses import dataclass
from typing import Type

from routers.auth.constants import PAGINATOR_ITEMS_PER_PAGE
from sql_app.models import Base


@dataclass
class Paginator:
    """ Paginator for users """
    items: list[Type[Base]]
    page: int = 1
    per_page: int = PAGINATOR_ITEMS_PER_PAGE

    @property
    def available_pages(self) -> int:
        full_pages = len(self.items) // self.per_page
        if full_pages * self.per_page == len(self.items):
            return full_pages
        return full_pages + 1

    @property
    def paginated_items(self) -> list:
        start = (self.page - 1) * self.per_page
        end = self.page * self.per_page
        try:
            return self.items[start: end]
        except IndexError:
            return self.items[start::]
