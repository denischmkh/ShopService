from enum import Enum


class AuthenticationUrls(str, Enum):
    registration = '/register'
    found_user_by_id_or_username = '/found_user'
    get_all_users_from_db = '/all_users'
    delete_user = '/delete_user'
    authorization = '/login'
    get_current_user_by_token = '/get_current_user'
    ban_user = '/ban_user'
    unban_user = '/unban_user'
