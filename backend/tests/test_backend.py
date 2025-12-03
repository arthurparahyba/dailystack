import unittest
import json
from app import server
from backend.api import load_daily_challenge

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.app = server.test_client()
        self.app.testing = True
        # Ensure data is loaded
        load_daily_challenge()

    def test_get_scenario(self):
        response = self.app.get('/api/scenario')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('title', data)
        self.assertIn('description', data)

    def test_get_current_flashcard(self):
        response = self.app.get('/api/flashcard/current')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertIn('question', data)

    def test_next_flashcard(self):
        # Get current
        r1 = self.app.get('/api/flashcard/current')
        d1 = json.loads(r1.data)
        
        # Next
        r2 = self.app.post('/api/flashcard/next')
        self.assertEqual(r2.status_code, 200)
        d2 = json.loads(r2.data)
        
        # Should be the same since we have only 1 mock card
        self.assertEqual(d1['question'], d2['question'])

    def test_ask_llm(self):
        response = self.app.post('/api/ask-llm', json={'question': 'Test?'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/event-stream')
        # Check if we get at least one data chunk
        self.assertIn(b'data:', response.data)

if __name__ == '__main__':
    unittest.main()
