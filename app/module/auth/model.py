from typing import Optional
from uuid import uuid4

from sqlalchemy import BINARY, Column, ForeignKey, UniqueConstraint
from sqlmodel import Field, Relationship