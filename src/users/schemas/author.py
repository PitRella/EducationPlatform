from src.base.schemas import BaseSchema


class CreateAuthorRequestSchema(BaseSchema):
    user_id: uuid.UUID
