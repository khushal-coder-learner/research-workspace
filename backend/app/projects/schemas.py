from __future__ import annotations

from typing import Annotated

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints


class ProjectCreate(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=1,
            max_length=255,
            strip_whitespace=True,
        ),
    ]
    description: str | None = None


class ProjectRead(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
