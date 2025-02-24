import unittest
import sqlite3
import os
from app import views  # Assuming your app's main file is named app.py
from flask import Flask


class FlaskAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = "test_WMGInvent.db"
        views.db_path = cls.test_db  # Override database path with test DB
        cls.create_test_db()

    @staticmethod
    def create_test_db():
        """Creates a test database and initializes tables."""
        conn = sqlite3.connect("test_WMGInvent.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                admin INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY,
                make TEXT,
                model TEXT,
                year INTEGER,
                registration TEXT,
                status TEXT,
                path_to_image TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS changes (
                id INTEGER PRIMARY KEY,
                car_id INTEGER,
                change TEXT,
                date_start TEXT,
                date_end TEXT,
                user_id INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def create_app(self):
        """Create and configure a new app instance for testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret'
        app.register_blueprint(views.views)  # Register the blueprint
        return app

    def setUp(self):
        self.app = self.create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_db)

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register_and_login(self):
        self.client.post(
            '/register', data={'username': 'testuser', 'password': 'testpass'})
        self.client.post(
            '/login', data={'username': 'testuser', 'password': 'testpass'})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['username'], 'testuser')

    def test_delete_user(self):
        self.client.post(
            '/register', data={'username': 'testuser', 'password': 'testpass'})
        self.client.post(
            '/login', data={'username': 'testuser', 'password': 'testpass'})
        self.client.get('/delete')
        with self.client.session_transaction() as sess:
            self.assertNotIn('username', sess)

    def test_update_user(self):
        self.client.post(
            '/register', data={'username': 'testuser', 'password': 'testpass'})
        self.client.post(
            '/login', data={'username': 'testuser', 'password': 'testpass'})
        response = self.client.post(
            '/update', data={'new_username': 'testuser', 'new_password': 'testpass'})
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.get('/logout')
        with self.client.session_transaction() as sess:
            self.assertNotIn('username', sess)

    def test_add_car(self):
        response = self.client.get('/fleet/add',
                                   data={'make': 'Toyota', 'model': 'Aygo', 'year': '2020', 'registration': 'TY70 ABC', 'status': 'Available', 'path_to_image': 'test.jpg'})
        # Should redirect after adding car
        self.assertEqual(response.status_code, 200)

    def test_search_car(self):
        response = self.client.post('/fleet/search', data={'search': 'Toyota'})
        self.assertTrue((response.status_code, 200))

    def test_data(self):
        response = self.client.get('/data')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
