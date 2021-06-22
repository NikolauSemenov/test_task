from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///test.db', echo=False)


class DatabaseTransaction(object):
    """
    Контекстный Менеджер для подключения к БД.
    """

    def __init__(self, name_db: str):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def __enter__(self):
        """
        Подключение к базе данных
        """
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Закрываем подключение
        """
        if exc_val and str(exc_val) == "rollback":
            # Так подавляем исключение, вызванное исскуственно.
            self.session.rollback()
            self.session.close()
            return True
        elif exc_type is not None:
            self.session.rollback()
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
        finally:
            self.session.close()
