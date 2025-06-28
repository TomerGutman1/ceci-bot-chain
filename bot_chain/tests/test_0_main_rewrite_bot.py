"""
Unit and golden tests for 0_MAIN_REWRITE_BOT.
"""
import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime
import sys
import os

# Add bot_chain to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

# Mock environment variables before importing
with patch.dict(os.environ, {
    'OPENAI_API_KEY': 'sk-test-key',
    'SUPABASE_URL': 'https://test.supabase.co',
    'SUPABASE_SERVICE_KEY': 'test-service-key'
}):
    from bot_chain.rewrite_bot.main import app, call_gpt


class TestRewriteBot(unittest.TestCase):
    """Test the Rewrite Bot API."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
        self.conv_id = str(uuid4())
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["layer"], "0_MAIN_REWRITE_BOT")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("uptime_seconds", data)
        self.assertIn("timestamp", data)
    
    @patch('bot_chain.rewrite_bot.main.call_gpt')
    def test_rewrite_success(self, mock_gpt):
        """Test successful text rewriting."""
        # Mock GPT response
        mock_gpt.return_value = {
            "result": {
                "clean_text": "החלטות ממשלה 37 בנושא חינוך",
                "corrections": [
                    {
                        "type": "normalization",
                        "original": "ממשלה שלושים ושבע",
                        "corrected": "ממשלה 37"
                    }
                ]
            },
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
                "model": "gpt-3.5-turbo"
            }
        }
        
        # Test request
        payload = {
            "text": "תביא לי את ההחלטות של ממשלה שלושים ושבע בנושא חינוך",
            "conv_id": self.conv_id
        }
        
        response = self.client.post("/rewrite", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["conv_id"], self.conv_id)
        self.assertEqual(data["clean_text"], "החלטות ממשלה 37 בנושא חינוך")
        self.assertEqual(data["original_text"], payload["text"])
        self.assertEqual(data["layer"], "0_MAIN_REWRITE_BOT")
        
        # Check corrections
        self.assertEqual(len(data["corrections"]), 1)
        correction = data["corrections"][0]
        self.assertEqual(correction["type"], "normalization")
        self.assertEqual(correction["original"], "ממשלה שלושים ושבע")
        self.assertEqual(correction["corrected"], "ממשלה 37")
        
        # Check token usage
        token_usage = data["token_usage"]
        self.assertEqual(token_usage["total_tokens"], 150)
        self.assertEqual(token_usage["model"], "gpt-3.5-turbo")
    
    def test_rewrite_missing_text(self):
        """Test rewrite with missing text field."""
        payload = {
            "conv_id": self.conv_id
            # Missing 'text' field
        }
        
        response = self.client.post("/rewrite", json=payload)
        self.assertEqual(response.status_code, 422)  # Validation error
    
    def test_rewrite_invalid_conv_id(self):
        """Test rewrite with invalid conversation ID."""
        payload = {
            "text": "שלום",
            "conv_id": "invalid-uuid"
        }
        
        response = self.client.post("/rewrite", json=payload)
        self.assertEqual(response.status_code, 422)  # Validation error
    
    @patch('bot_chain.rewrite_bot.main.call_gpt')
    def test_rewrite_gpt_failure(self, mock_gpt):
        """Test rewrite when GPT call fails."""
        mock_gpt.side_effect = Exception("OpenAI API error")
        
        payload = {
            "text": "בדיקה",
            "conv_id": self.conv_id
        }
        
        response = self.client.post("/rewrite", json=payload)
        self.assertEqual(response.status_code, 500)
        
        data = response.json()
        self.assertIn("error", data)


class TestGPTCall(unittest.TestCase):
    """Test GPT calling functionality."""
    
    @patch('openai.ChatCompletion.create')
    def test_call_gpt_success(self, mock_openai):
        """Test successful GPT call."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "clean_text": "טקסט נקי",
            "corrections": []
        })
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 25
        mock_response.usage.total_tokens = 75
        
        mock_openai.return_value = mock_response
        
        # Run test
        result = asyncio.run(call_gpt("טקסט לבדיקה"))
        
        self.assertIn("result", result)
        self.assertIn("usage", result)
        self.assertEqual(result["result"]["clean_text"], "טקסט נקי")
        self.assertEqual(result["usage"]["total_tokens"], 75)
    
    @patch('openai.ChatCompletion.create')
    def test_call_gpt_invalid_json(self, mock_openai):
        """Test GPT call with invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid JSON"
        
        mock_openai.return_value = mock_response
        
        # Should raise HTTPException
        with self.assertRaises(Exception):
            asyncio.run(call_gpt("טקסט"))
    
    @patch('openai.ChatCompletion.create')
    def test_call_gpt_api_error(self, mock_openai):
        """Test GPT call with API error."""
        mock_openai.side_effect = Exception("API rate limit exceeded")
        
        with self.assertRaises(Exception):
            asyncio.run(call_gpt("טקסט"))


class TestGoldenCases(unittest.TestCase):
    """Golden test cases for text rewriting."""
    
    def setUp(self):
        """Set up test client."""
        self.client = TestClient(app)
        self.conv_id = str(uuid4())
    
    @patch('bot_chain.rewrite_bot.main.call_gpt')
    def test_golden_case_government_number_normalization(self, mock_gpt):
        """Test normalization of government numbers."""
        mock_gpt.return_value = {
            "result": {
                "clean_text": "החלטות ממשלה 37",
                "corrections": [
                    {
                        "type": "normalization",
                        "original": "ממשלה שלושים ושבע",
                        "corrected": "ממשלה 37"
                    }
                ]
            },
            "usage": {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75, "model": "gpt-3.5-turbo"}
        }
        
        test_cases = [
            "החלטות ממשלה שלושים ושבע",
            "ממשלה שלושים וחמש החלטה 660",
            "החלטה מספר אלף ושלוש מאות של ממשלה שלושים ושבע"
        ]
        
        for text in test_cases:
            with self.subTest(text=text):
                payload = {"text": text, "conv_id": self.conv_id}
                response = self.client.post("/rewrite", json=payload)
                
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn("clean_text", data)
                self.assertIn("corrections", data)
    
    @patch('bot_chain.rewrite_bot.main.call_gpt')
    def test_golden_case_spelling_correction(self, mock_gpt):
        """Test spelling corrections."""
        mock_gpt.return_value = {
            "result": {
                "clean_text": "החלטות ממשלה בנושא חינוך",
                "corrections": [
                    {
                        "type": "spelling",
                        "original": "חינוך",
                        "corrected": "חינוך"
                    }
                ]
            },
            "usage": {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75, "model": "gpt-3.5-turbo"}
        }
        
        payload = {
            "text": "החלטות ממשלה בנושא חינוק",  # Misspelled word
            "conv_id": self.conv_id
        }
        
        response = self.client.post("/rewrite", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["clean_text"], "החלטות ממשלה בנושא חינוך")
    
    @patch('bot_chain.rewrite_bot.main.call_gpt')
    def test_golden_case_no_changes_needed(self, mock_gpt):
        """Test when no corrections are needed."""
        original_text = "החלטה 660 ממשלה 37"
        
        mock_gpt.return_value = {
            "result": {
                "clean_text": original_text,
                "corrections": []
            },
            "usage": {"prompt_tokens": 40, "completion_tokens": 20, "total_tokens": 60, "model": "gpt-3.5-turbo"}
        }
        
        payload = {
            "text": original_text,
            "conv_id": self.conv_id
        }
        
        response = self.client.post("/rewrite", json=payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["clean_text"], original_text)
        self.assertEqual(len(data["corrections"]), 0)


if __name__ == '__main__':
    unittest.main()