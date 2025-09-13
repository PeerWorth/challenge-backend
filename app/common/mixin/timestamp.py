from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.common.enums import Timezone
from app.common.utils.time import TimeConverter, utc_now


class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False, sa_column_kwargs={"onupdate": utc_now})
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    is_deleted: bool = Field(default=False, nullable=False)

    @property
    def created_at_kst(self):
        return TimeConverter.from_db(self.created_at, Timezone.KST)
