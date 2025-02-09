import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import io
from ..main import app

class TestRouters(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_file_content = b"Test document content"
        self.test_file = io.BytesIO(self.test_file_content)

    @patch('routers.DocumentHandler')
    @patch('routers.MLService')
    async def test_successful_upload(self, mock_ml, mock_doc_handler):
        mock_ml.classify_document.return_value = {
            'category': 'Test',
            'predictions': [{'confidence': 0.9}]
        }
        mock_doc = MagicMock(filename='test.txt')
        mock_doc_handler.return_value.create_document.return_value = mock_doc

        files = {'file': ('test.txt', self.test_file, 'text/plain')}
        response = self.client.post("/upload", files=files)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['filename'], 'test.txt')
        self.assertEqual(len(response.json()['predictions']), 1)

    @patch('routers.DocumentHandler')
    async def test_upload_invalid_file(self, mock_doc_handler):
        invalid_content = b'\x80\x81'
        files = {'file': ('test.txt', io.BytesIO(invalid_content), 'text/plain')}
        
        response = self.client.post("/upload", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file encoding", response.json()['detail'])

    @patch('routers.DocumentHandler')
    @patch('os.remove')
    async def test_upload_db_error(self, mock_remove, mock_doc_handler):
        mock_doc_handler.return_value.create_document.side_effect = Exception("DB Error")
        
        files = {'file': ('test.txt', self.test_file, 'text/plain')}
        response = self.client.post("/upload", files=files)
        
        self.assertEqual(response.status_code, 500)
        mock_remove.assert_called_once()

    @patch('routers.DocumentHandler')
    async def test_get_documents_success(self, mock_doc_handler):
        mock_docs = [
            MagicMock(
                id=1,
                filename="test1.txt",
                category="Category1",
                confidence=0.9,
                upload_time="2023-01-01"
            ),
            MagicMock(
                id=2, 
                filename="test2.txt",
                category="Category2",
                confidence=0.8,
                upload_time="2023-01-02"
            )
        ]
        mock_doc_handler.return_value.get_all_documents.return_value = mock_docs

        response = self.client.get("/get_documents")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]['filename'], "test1.txt")
        self.assertEqual(response.json()[1]['category'], "Category2")

    @patch('routers.DocumentHandler') 
    async def test_get_documents_empty(self, mock_doc_handler):
        mock_doc_handler.return_value.get_all_documents.return_value = []
        
        response = self.client.get("/get_documents")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 0)

    @patch('routers.DocumentHandler')
    async def test_get_documents_error(self, mock_doc_handler):
        mock_doc_handler.return_value.get_all_documents.side_effect = Exception("DB Error")
        
        with self.assertRaises(Exception):
            self.client.get("/get_documents")

    async def test_upload_no_file(self):
        response = self.client.post("/upload")
        self.assertEqual(response.status_code, 422)

    @patch('os.path.join')
    async def test_upload_filesystem_error(self, mock_join):
        mock_join.side_effect = OSError("File system error")
        
        files = {'file': ('test.txt', self.test_file, 'text/plain')}
        response = self.client.post("/upload", files=files)
        
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()