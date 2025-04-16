from sqlalchemy import Column, Integer, String, Text, Date, JSON
from .database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    birth_date = Column(Date, nullable=True)
    photo_path = Column(String(255), nullable=True)
    city = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    github = Column(String(100), nullable=True)

    position = Column(String(100))
    about = Column(Text, nullable=True)
    skills = Column(JSON, nullable=True)
    experience = Column(Text, nullable=True)
    education = Column(Text)
    courses = Column(JSON, nullable=True)
    languages = Column(JSON, nullable=True)

    created_at = Column(Date)
