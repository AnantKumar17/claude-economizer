#!/usr/bin/env python3
"""
Unit tests for prompt-economizer
Run: python3 -m pytest tests/test_economizer.py -v
"""

import unittest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks"))

import economizer


class TestTokenEstimation(unittest.TestCase):
    """Test token estimation function"""

    def test_estimate_tokens_basic(self):
        # Test basic estimation
        text = "This is a simple test"
        tokens = economizer.estimate_tokens(text)
        # 5 words / 0.75 = ~6.67 = 6 tokens
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, 20)

    def test_estimate_tokens_empty(self):
        tokens = economizer.estimate_tokens("")
        self.assertEqual(tokens, 1)  # min 1 token


class TestHeuristicClassification(unittest.TestCase):
    """Test heuristic classification logic"""

    def setUp(self):
        self.config = {
            "bypass_prefixes": ["*", "//", "##", "#noopt"],
            "short_prompt_threshold_tokens": 8,
            "large_task_threshold_tokens": 120
        }

    def test_bypass_prefix_star(self):
        prompt = "* this should bypass"
        result = economizer.heuristic_classify(prompt, self.config)
        self.assertEqual(result, "passthrough")

    def test_bypass_prefix_double_slash(self):
        prompt = "// this should bypass"
        result = economizer.heuristic_classify(prompt, self.config)
        self.assertEqual(result, "passthrough")

    def test_short_prompt(self):
        prompt = "help"
        result = economizer.heuristic_classify(prompt, self.config)
        self.assertEqual(result, "passthrough")

    def test_small_pattern_fix(self):
        # Add extra words to get above threshold
        prompt = "fix the bug in auth.py line 42 that causes null pointer"
        result = economizer.heuristic_classify(prompt, self.config)
        self.assertEqual(result, "small")

    def test_small_pattern_rename(self):
        # Add extra words to get above threshold
        prompt = "rename function getUserData to fetchUserData in utils.js"
        result = economizer.heuristic_classify(prompt, self.config)
        self.assertEqual(result, "small")

    def test_large_with_keywords(self):
        # Create a long prompt with large keywords
        prompt = "architect a complete microservice from scratch " + " ".join(["word"] * 100)
        result = economizer.heuristic_classify(prompt, self.config)
        self.assertEqual(result, "large")

    def test_inconclusive(self):
        # Medium complexity prompt that needs LLM
        prompt = "I need to update the authentication system to support OAuth2"
        result = economizer.heuristic_classify(prompt, self.config)
        self.assertIsNone(result)  # Should be inconclusive


class TestStatsTracking(unittest.TestCase):
    """Test stats tracking functionality"""

    @patch('economizer.Path')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_stats_new_file(self, mock_file, mock_path):
        config = {"stats_enabled": True, "stats_file": "~/test/stats.json"}
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        # This should not crash
        economizer.update_stats("small", 100, 60, 1500, config)

    @patch('economizer.Path')
    def test_update_stats_disabled(self, mock_path):
        config = {"stats_enabled": False}
        # Should return early without doing anything
        economizer.update_stats("small", 100, 60, 1500, config)
        # If it reaches here without error, the test passes


class TestOutputAnnotation(unittest.TestCase):
    """Test output annotation generation"""

    def setUp(self):
        self.config = {
            "show_diff": True,
            "show_savings_estimate": True
        }

    def test_annotation_small_tier(self):
        original = "hey could you maybe fix the bug in auth.py"
        optimized = "Fix bug in auth.py"
        result = economizer.build_output_with_annotation(
            original, optimized, "small", 1500, self.config
        )
        self.assertIn("prompt-economizer", result)
        self.assertIn("tier=small", result)
        self.assertIn("compressed", result)
        self.assertIn(optimized, result)

    def test_annotation_medium_tier(self):
        original = "update the login system"
        optimized = "<task>Update login system</task>"
        result = economizer.build_output_with_annotation(
            original, optimized, "medium", 2000, self.config
        )
        self.assertIn("restructured", result)
        self.assertIn("downstream", result)

    def test_no_annotation_when_disabled(self):
        config = {"show_diff": False, "show_savings_estimate": False}
        original = "fix bug"
        optimized = "Fix bug"
        result = economizer.build_output_with_annotation(
            original, optimized, "small", 1000, config
        )
        self.assertEqual(result, optimized)

    def test_passthrough_tier(self):
        original = "help"
        optimized = "help"
        result = economizer.build_output_with_annotation(
            original, optimized, "passthrough", 100, self.config
        )
        self.assertEqual(result, optimized)


class TestMainIntegration(unittest.TestCase):
    """Test main function integration"""

    @patch('sys.stdin')
    @patch('sys.stdout')
    @patch('economizer.load_config')
    @patch('economizer.setup_logging')
    def test_main_mode_off(self, mock_logging, mock_config, mock_stdout, mock_stdin):
        mock_config.return_value = {"mode": "off"}
        test_input = '{"prompt": "test prompt"}'
        mock_stdin.read.return_value = test_input

        economizer.main()

        # Should pass through unchanged
        mock_stdout.write.assert_called_once_with(test_input)

    @patch('sys.stdin')
    @patch('builtins.print')
    @patch('economizer.load_config')
    @patch('economizer.setup_logging')
    def test_main_empty_prompt(self, mock_logging, mock_config, mock_print, mock_stdin):
        mock_config.return_value = {"mode": "auto"}
        test_input = '{"prompt": ""}'
        mock_stdin.read.return_value = test_input

        with patch('sys.stdout.write') as mock_write:
            economizer.main()
            mock_write.assert_called_once_with(test_input)

    @patch('sys.stdin')
    @patch('builtins.print')
    @patch('economizer.load_config')
    @patch('economizer.setup_logging')
    @patch('economizer.heuristic_classify')
    @patch('os.environ.get')
    def test_main_passthrough_classification(self, mock_env, mock_classify,
                                            mock_logging, mock_config, mock_print, mock_stdin):
        mock_config.return_value = {
            "mode": "auto",
            "stats_enabled": False,
            "show_diff": False,
            "api_key_env_var": "ANTHROPIC_API_KEY"
        }
        mock_env.return_value = "test-key"
        mock_classify.return_value = "passthrough"
        test_input = '{"prompt": "help"}'
        mock_stdin.read.return_value = test_input

        economizer.main()

        # Should output the original prompt
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any("help" in call for call in calls))


if __name__ == "__main__":
    unittest.main()
