from src.base.dao import BaseDAO
from src.users import Author
from src.users.schemas import CreateAuthorRequestSchema


class AuthorDAO(BaseDAO[Author, CreateAuthorRequestSchema]):
    pass