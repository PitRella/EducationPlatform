from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base Pydantic model for all schemas."""

    model_config = ConfigDict(from_attributes=True)
