from sqlalchemy.orm import Session

from app.models.class_model import Class



class ClassService:

    @staticmethod
    def get_all_classes(db: Session):
        return db.query(Class).order_by(Class.name).all()

    @staticmethod
    def get_class_by_id(db: Session, class_id):
        return (
            db.query(Class)
            .filter(Class.id == class_id)
            .first()
        )