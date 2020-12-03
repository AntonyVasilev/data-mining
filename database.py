from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import db_model


class GBDataBase:
    def __init__(self, db_url: str):
        engine = create_engine(db_url)
        db_model.Base.metadata.create_all(bind=engine)
        self.session_m = sessionmaker(bind=engine)

    @staticmethod
    def _get_or_create(session, model, data):
        db_model = session.query(model).filter(model.url == data['url']).first()
        if not db_model:
            db_model = model(**data)
        return db_model

    @staticmethod
    def _get_or_create_tags(session, model, data):
        for el in data:
            db_model = session.query(model).filter(model.url == el['url']).first()
            if not db_model:
                db_model = model(**data)
            return db_model

    def create_post(self, data):
        session = self.session_m()
        writer = self._get_or_create(session, models.Writer, data.pop('writer'))
        tags = self._get_or_create_tags(session, models.Tag, data.pop('tags'))
        post = self._get_or_create(session, models.Post, data)
        post.writer = writer
        post.tags = tags
        session.add(post)

        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
        finally:
            session.close()

        print(1)