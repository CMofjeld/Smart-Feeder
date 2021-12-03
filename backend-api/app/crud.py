"""Functions to perform CRUD operations on the database."""
from typing import List
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app import models


def get_user_by_username(db: Session, username: str) -> models.User:
    """Return user with matching username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_top_visiting_birds(db: Session, limit: int = 10):
    """Return the top visiting birds and their visit count."""
    return db.query(
        models.Bird.common_name,func.count(models.Bird.common_name).label('num_visits')
        ).join(
            models.Visit, models.Visit.visiting_bird==models.Bird.id
        ).group_by(
            models.Bird.common_name
        ).order_by(
            desc("num_visits"), models.Bird.common_name
        ).limit(
            limit
        ).all()
