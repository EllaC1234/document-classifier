from typing import List, Dict, Any
import logging
from transformers import pipeline
from config import settings

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        """Initialize the ML service with the classification model"""
        self.classifier = pipeline(
            "zero-shot-classification", 
            model=settings.MODEL_NAME
        )
        self.candidate_labels = settings.CANDIDATE_LABELS

    def classify_document(self, text: str) -> Dict[str, Any]:
        """
        Classify a document text into predefined categories
        """
        if len(text.strip()) <= settings.CHUNK_SIZE:
            return self._classify_single_chunk(text)
        return self._classify_multiple_chunks(text)

    def _classify_single_chunk(self, text: str) -> Dict[str, Any]:
        """
        Classify a single chunk of text
        """
        result = self.classifier(text, self.candidate_labels, multi_label=False)
        return {
            'category': result['labels'][0],
            'predictions': [
                {"category": label, "confidence": score}
                for label, score in zip(result['labels'], result['scores'])
            ]
        }

    def _classify_multiple_chunks(self, text: str) -> Dict[str, Any]:
        """
        Classify a document by breaking it into chunks and aggregating results
        """
        chunks = [
            text[i:i + settings.CHUNK_SIZE] 
            for i in range(0, len(text), settings.CHUNK_SIZE)
        ]
        chunk_results = self._process_chunks(chunks)

        if not chunk_results:
            return self._get_default_classification()

        averaged_scores = self._calculate_average_scores(chunk_results)
        return self._format_predictions(averaged_scores)

    def _process_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """
        Process each chunk and collect classification results
        """
        chunk_results = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Classifying chunk {i+1} of {len(chunks)}...")
            try:
                result = self.classifier(chunk, self.candidate_labels, multi_label=False)
                chunk_results.append({
                    'labels': result['labels'],
                    'scores': result['scores']
                })
            except Exception as e:
                logger.error(f"Error classifying chunk {i+1}: {e}")
                continue
        return chunk_results

    def _get_default_classification(self) -> Dict[str, Any]:
        """
        Return default classification when processing fails
        """
        return {
            'category': 'Other',
            'predictions': [
                {"category": label, "confidence": 0.0}
                for label in self.candidate_labels
            ]
        }

    def _calculate_average_scores(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate average scores across all chunks
        """
        label_scores = {label: [] for label in self.candidate_labels}
        
        for result in chunk_results:
            for label, score in zip(result['labels'], result['scores']):
                label_scores[label].append(score)
        
        averaged_scores = {}
        for label, scores in label_scores.items():
            if scores:
                averaged_scores[label] = sum(scores) / len(scores)
            else:
                averaged_scores[label] = 0.0
                
        return averaged_scores

    def _format_predictions(self, averaged_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Format the final predictions with sorted confidence scores
        """
        predictions = [
            {"category": label, "confidence": score}
            for label, score in averaged_scores.items()
        ]
        
        sorted_predictions = sorted(
            predictions,
            key=lambda x: x["confidence"],
            reverse=True
        )
        
        return {
            'category': sorted_predictions[0]['category'],
            'predictions': sorted_predictions
        }