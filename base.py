from aiohttp import web
from marshmallow import Schema
from marshmallow.exceptions import ValidationError
from multidict import MultiDictProxy
from sqlalchemy.orm import Session

import requests_db
import serelizator
from requests_db import logger


class BaseView(web.View):

    @staticmethod
    def load(data: MultiDictProxy, _schema: Schema) -> dict:
        try:
            return _schema.load(data)
        except ValidationError as e:
            logger.error(f"{e}")
            raise web.HTTPUnprocessableEntity(text=str(e.messages))

    @property
    def session(self) -> Session:
        return self.request.app["session_db"]

    @property
    def db(self) -> requests_db:
        return requests_db

    @property
    def schemas(self) -> serelizator:
        return serelizator
