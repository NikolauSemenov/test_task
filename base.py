from aiohttp import web
from marshmallow import Schema
from typing import Any
from sqlalchemy.orm import Session

import requests_db
import serelizator


class BaseView(web.View):

    @property
    def session(self) -> Session:
        return self.request.session

    @property
    def db(self) -> requests_db:
        return requests_db

    @property
    def schemas(self) -> serelizator:
        return serelizator

    @staticmethod
    def dump(data: Any, schema_: Schema):
        return schema_.dump(data)
