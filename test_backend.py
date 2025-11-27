import unittest
import json
from app import server, load_daily_challenge

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.app = server.test_client()
        self.app.testing = True
        # Ensure data is loaded
        load_daily_challenge()

    def test_get_scenario(self):
        response = self.app.get('/scenario')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('title', data)
        self.assertIn('description', data)

    def test_get_current_flashcard(self):
        response = self.app.get('/flashcard/current')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('title', data)
        self.assertIn('question', data)

    def test_next_flashcard(self):
        # Get current
        r1 = self.app.get('/flashcard/current')
        d1 = json.loads(r1.data)
        
        # Next
        r2 = self.app.post('/flashcard/next')
        self.assertEqual(r2.status_code, 200)
        d2 = json.loads(r2.data)
        
        # Should be different or same if only 1 (but we have 3 mock cards)
        self.assertNotEqual(d1['title'], d2['title'])

    def test_ask_llm(self):
        response = self.app.post('/ask-llm', json={'question': 'Test?'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('answer', data)

if __name__ == '__main__':
    unittest.main()
