import os
import unittest
from epub_to_html_converter import EPUBToHTMLConverter

class TestEPUBConverter(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test outputs
        self.test_output_dir = 'test_epub_output'
        os.makedirs(self.test_output_dir, exist_ok=True)
    
    def test_converter_initialization(self):
        """Test basic initialization of converter"""
        # Note: Replace with a sample EPUB path for testing
        sample_epub = 'sample_book.epub'
        
        if os.path.exists(sample_epub):
            converter = EPUBToHTMLConverter(sample_epub, output_dir=self.test_output_dir)
            self.assertTrue(os.path.exists(self.test_output_dir))
            self.assertEqual(converter.output_dir, self.test_output_dir)
    
    def test_metadata_extraction(self):
        """Test metadata extraction"""
        # Note: Replace with a sample EPUB path for testing
        sample_epub = 'sample_book.epub'
        
        if os.path.exists(sample_epub):
            converter = EPUBToHTMLConverter(sample_epub)
            converter.convert()  # Ensure book is loaded
            
            metadata = converter.get_book_metadata()
            self.assertIn('title', metadata)
            self.assertIn('creator', metadata)
    
    def tearDown(self):
        # Clean up test output directory
        if os.path.exists(self.test_output_dir):
            for file in os.listdir(self.test_output_dir):
                os.remove(os.path.join(self.test_output_dir, file))
            os.rmdir(self.test_output_dir)

if __name__ == '__main__':
    unittest.main()
