import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DB_NAME = "sqlite:///./lectures.db"
engine = create_engine(DB_NAME, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Lecture(Base):
    __tablename__ = "lectures"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    transcript = Column(Text)
    summary = Column(Text)
    notes = Column(Text)
    quiz = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_lecture(filename, transcript, materials):
    db = SessionLocal()
    try:
        db_lecture = Lecture(
            filename=filename,
            transcript=transcript,
            summary=materials['summary'],
            notes=json.dumps(materials['notes']),
            quiz=json.dumps(materials['quiz'])
        )
        db.add(db_lecture)
        db.commit()
        db.refresh(db_lecture)
        return db_lecture.id
    finally:
        db.close()

def get_all_lectures():
    db = SessionLocal()
    try:
        lectures = db.query(Lecture).order_by(Lecture.created_at.desc()).all()
        return [{"id": r.id, "filename": r.filename, "date": r.created_at.isoformat()} for r in lectures]
    finally:
        db.close()

def get_lecture_by_id(lecture_id):
    db = SessionLocal()
    try:
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if lecture:
            return {
                "id": lecture.id,
                "filename": lecture.filename,
                "transcript": lecture.transcript,
                "materials": {
                    "summary": lecture.summary,
                    "notes": json.loads(lecture.notes),
                    "quiz": json.loads(lecture.quiz)
                },
                "date": lecture.created_at.isoformat()
            }
        return None
    finally:
        db.close()

def delete_lecture(lecture_id):
    db = SessionLocal()
    try:
        db.query(Lecture).filter(Lecture.id == lecture_id).delete()
        db.commit()
    finally:
        db.close()
