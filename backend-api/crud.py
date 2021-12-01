"""Functions to perform CRUD operations on the database."""
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from models import Bird, Visit

def get_top_visiting_birds(db: Session, limit: int = 10):
    """Return the top visiting birds and their visit count."""
    return db.query(Bird.common_name, func.count(Bird.common_name).label('num_visits')).join(Visit, Visit.visiting_bird==Bird.id).group_by(Bird.common_name).order_by(desc("num_visits"), Bird.common_name).limit(limit).all()