import os
import json
import unittest
import app
from flask_sqlalchemy import SQLAlchemy
import database.models as models


class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.app
        self.client = self.app.test_client

        self.database_path = models.database_path
        models.setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        pass

    def test_index(self):
        res = self.cient.get('/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)


if __name__ == 'main':
    unittest.main()
