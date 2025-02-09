import unittest
from unittest.mock import Mock, patch
from ml_service import MLService

class TestMLService(unittest.TestCase):
    def setUp(self):
        self.ml_service = MLService()
        self.sample_text = "This is a test document"
        self.mock_labels = ["Category1", "Category2"]
        self.ml_service.candidate_labels = self.mock_labels

    @patch('ml_service.pipeline')
    def test_init(self, mock_pipeline):
        """Test MLService initialization"""
        MLService()
        mock_pipeline.assert_called_once()

    def test_classify_single_chunk(self):
        """Test classification of text shorter than chunk size"""
        self.ml_service.classifier = Mock()
        self.ml_service.classifier.return_value = {
            'labels': ['Category1', 'Category2'],
            'scores': [0.8, 0.2]
        }

        result = self.ml_service.classify_document("Short text")
        self.assertEqual(result['category'], 'Category1')
        self.assertEqual(len(result['predictions']), 2)

    def test_classify_multiple_chunks(self):
        """Test classification of text longer than chunk size"""
        self.ml_service.classifier = Mock()
        self.ml_service.classifier.return_value = {
            'labels': ['Category1', 'Category2'],
            'scores': [0.7, 0.3]
        }

        long_text = "Long text" * 1000
        result = self.ml_service.classify_document(long_text)
        self.assertIn('category', result)
        self.assertIn('predictions', result)

    def test_process_chunks_error(self):
        """Test chunk processing with errors"""
        self.ml_service.classifier = Mock()
        self.ml_service.classifier.side_effect = Exception("Test error")

        result = self.ml_service._process_chunks(["chunk1", "chunk2"])
        self.assertEqual(result, [])

    def test_default_classification(self):
        """Test default classification response"""
        result = self.ml_service._get_default_classification()
        self.assertEqual(result['category'], 'Other')
        self.assertEqual(len(result['predictions']), len(self.mock_labels))

    def test_calculate_average_scores(self):
        """Test score averaging across chunks"""
        chunk_results = [
            {'labels': ['Category1', 'Category2'], 'scores': [0.8, 0.2]},
            {'labels': ['Category1', 'Category2'], 'scores': [0.6, 0.4]}
        ]
        result = self.ml_service._calculate_average_scores(chunk_results)
        self.assertEqual(result['Category1'], 0.7)

    def test_format_predictions(self):
        """Test prediction formatting and sorting"""
        scores = {'Category1': 0.3, 'Category2': 0.7}
        result = self.ml_service._format_predictions(scores)
        self.assertEqual(result['category'], 'Category2')
        self.assertEqual(result['predictions'][0]['confidence'], 0.7)

if __name__ == '__main__':
    unittest.main()