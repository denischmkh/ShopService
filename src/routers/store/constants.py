from enum import Enum


class CategoryUrls(str, Enum):
    get_all_categories = '/get_categories'
    create_category = '/create'
    delete_category = '/delete'