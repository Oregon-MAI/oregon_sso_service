from sqlalchemy import UUID, Column, ForeignKey

from src.data.models.base import Base


class UserRole(Base):
    """
    Модель связи многие-ко-многим между пользователями и ролями
    """

    __tablename__ = "user_roles"
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
