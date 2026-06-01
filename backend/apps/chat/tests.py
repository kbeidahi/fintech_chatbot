import json
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.chat import multilingual_engine
from apps.chat.multilingual_engine import detect_language, gemini_fallback


class _FakeGeminiResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps({
            'candidates': [{
                'content': {
                    'parts': [{'text': 'Mocked Gemini answer'}],
                },
            }],
        }).encode('utf-8')


class GeminiFallbackTests(SimpleTestCase):
    @override_settings(GEMINI_API_KEY='test-key', GEMINI_MODEL='gemini-test-model')
    def test_gemini_fallback_allows_general_questions(self):
        captured = {}

        def fake_urlopen(request, timeout):
            captured['url'] = request.full_url
            captured['body'] = json.loads(request.data.decode('utf-8'))
            captured['timeout'] = timeout
            return _FakeGeminiResponse()

        with patch.object(multilingual_engine.urllib.request, 'urlopen', fake_urlopen):
            answer = gemini_fallback('What is the capital of France?', 'en')

        self.assertEqual(answer, 'Mocked Gemini answer')
        self.assertEqual(captured['timeout'], 15)
        self.assertIn('/v1beta/models/gemini-test-model:generateContent', captured['url'])
        self.assertEqual(captured['body']['contents'][0]['role'], 'user')
        prompt = captured['body']['system_instruction']['parts'][0]['text']
        self.assertIn('reasonable general questions', prompt)
        self.assertIn('Do not execute financial transactions', prompt)

    @override_settings(GEMINI_API_KEY='test-key', OPENAI_API_KEY='')
    def test_resolve_uses_gemini_when_faq_does_not_match(self):
        with (
            patch.object(
                multilingual_engine.MultilingualIntentEngine,
                '_match_faq',
                return_value=(None, 0.0),
            ),
            patch.object(
                multilingual_engine,
                'gemini_fallback',
                return_value='Gemini handled this out-of-FAQ question',
            ),
        ):
            result = multilingual_engine.multilingual_engine.resolve(
                'What is the capital of France?'
            )

        self.assertEqual(result['source'], 'gemini')
        self.assertEqual(result['answer'], 'Gemini handled this out-of-FAQ question')

    @override_settings(GEMINI_API_KEY='', OPENAI_API_KEY='')
    def test_random_question_does_not_match_faq_by_question_similarity(self):
        result = multilingual_engine.multilingual_engine.resolve(
            'Write a haiku about sunrise over the ocean'
        )

        self.assertEqual(result['source'], 'fallback')
        self.assertEqual(result['intent'], 'unknown')

    @override_settings(GEMINI_API_KEY='', OPENAI_API_KEY='')
    def test_keyword_question_still_matches_faq(self):
        result = multilingual_engine.multilingual_engine.resolve(
            'What fees do you charge?'
        )

        self.assertEqual(result['source'], 'faq')
        self.assertEqual(result['intent'], 'tax')

    def test_english_words_containing_french_short_words_stay_english(self):
        self.assertEqual(detect_language('How do I transfer money?'), 'en')
