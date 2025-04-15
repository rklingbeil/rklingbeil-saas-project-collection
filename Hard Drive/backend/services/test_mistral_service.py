# File: /Users/rick/CaseProject/backend/services/test_mistral_service.py
import unittest
from mistral_service import analyze_case

class TestMistralService(unittest.TestCase):
    def test_analyze_case(self):
        sample_case = "Test legal case input."
        result = analyze_case(sample_case)
        # Check that result is a non-empty string
        self.assertTrue(isinstance(result, str) and len(result) > 0)

if __name__ == '__main__':
    unittest.main()

