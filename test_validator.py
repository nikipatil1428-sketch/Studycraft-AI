"""
Unit tests for StudyCraft AI input validation guardrails.
"""
import unittest

# Import directly from validator.py in the same folder
try:
    from validator import validate_input, validate_qa_pair, get_text_stats, clean_input
except ModuleNotFoundError:
    from services.validator import validate_input, validate_qa_pair, get_text_stats, clean_input


class TestValidator(unittest.TestCase):
    def test_empty_input(self):
        result = validate_input("")
        self.assertFalse(result.is_valid)
        self.assertIn("cannot be empty", result.error_message)

    def test_whitespace_only(self):
        result = validate_input("    \n\t   ")
        self.assertFalse(result.is_valid)

    def test_too_short(self):
        result = validate_input("Hello", min_chars=15)
        self.assertFalse(result.is_valid)
        self.assertIn("too short", result.error_message)

    def test_too_long(self):
        huge_text = "word " * 3000
        result = validate_input(huge_text, max_chars=500)
        self.assertFalse(result.is_valid)

    def test_repetitive_spam(self):
        spam = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        result = validate_input(spam)
        self.assertFalse(result.is_valid)

    def test_valid_input(self):
        valid_text = "This is a legitimate academic note about mitochondrial respiration and ATP production."
        result = validate_input(valid_text)
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_message)

    def test_text_stats(self):
        text = "Photosynthesis converts solar energy into chemical energy."
        stats = get_text_stats(text)
        self.assertEqual(stats["word_count"], 7)

    def test_clean_input(self):
        raw = "  \r\n  Line 1\r\nLine 2   "
        self.assertEqual(clean_input(raw), "Line 1\nLine 2")

    def test_validate_qa_pair(self):
        res = validate_qa_pair(
            "What is the function of the mitochondria in cells?",
            "Mitochondria produce ATP through the process of cellular respiration."
        )
        self.assertTrue(res.is_valid)


if __name__ == "__main__":
    unittest.main()
    