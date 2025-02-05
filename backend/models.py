from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())  # Automatically set to current time
    people_count = Column(Integer)
    visualized_image_path = Column(String)

    def __repr__(self):
        return f"<Detection(id={self.id}, people_count={self.people_count}, visualized_image_path={self.visualized_image_path})>"