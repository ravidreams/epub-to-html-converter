import os
import logging
import ebooklib
import base64
from ebooklib import epub
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EPUBToHTMLConverter:
    def __init__(self, epub_path, output_dir=None):
        """
        Initialize the EPUB to HTML converter
        
        :param epub_path: Path to the EPUB file
        :param output_dir: Directory to save HTML files (defaults to EPUB filename directory)
        """
        if not os.path.exists(epub_path):
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")
            
        self.epub_path = epub_path
        
        # Set output directory 
        if output_dir is None:
            output_dir = os.path.splitext(epub_path)[0] + '_html'
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'images'), exist_ok=True)
        
        # Book object
        self.book = None
        self.chapters = []
        self.images = {}
        
    def _save_images(self):
        """Extract and save images from EPUB"""
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                try:
                    # Create subdirectories if needed
                    image_name = item.get_name()
                    image_dir = os.path.dirname(image_name)
                    if image_dir:
                        full_image_dir = os.path.join(self.output_dir, 'images', image_dir)
                        os.makedirs(full_image_dir, exist_ok=True)
                    
                    image_path = os.path.join('images', image_name)
                    full_path = os.path.join(self.output_dir, image_path)
                    with open(full_path, 'wb') as f:
                        f.write(item.get_content())
                    self.images[image_name] = image_path
                    logger.info(f"Saved image: {image_path}")
                except Exception as e:
                    logger.error(f"Error saving image {image_name}: {str(e)}")

    def _process_images_in_content(self, content):
        """Process images in HTML content"""
        soup = BeautifulSoup(content, 'html.parser')
        for img in soup.find_all('image'):
            href = img.get('xlink:href')
            if href and href in self.images:
                img['xlink:href'] = '../' + self.images[href]
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and src in self.images:
                img['src'] = '../' + self.images[src]
        
        return str(soup)

    def _create_stylesheet(self):
        """Create a CSS file for styling"""
        css_content = """
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chapter-content {
            background-color: white;
            padding: 30px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .navigation {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav-button {
            text-decoration: none;
            padding: 8px 15px;
            background-color: #3498db;
            color: white;
            border-radius: 3px;
            transition: background-color 0.3s;
        }
        .nav-button:hover {
            background-color: #2980b9;
        }
        .toc {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .toc h1 {
            text-align: center;
            color: #2c3e50;
        }
        .toc-list {
            list-style-type: none;
            padding: 0;
        }
        .toc-list li {
            margin: 10px 0;
        }
        .toc-list a {
            text-decoration: none;
            color: #3498db;
            transition: color 0.3s;
        }
        .toc-list a:hover {
            color: #2980b9;
        }
        .chapter-title {
            text-align: center;
            margin-bottom: 30px;
        }
        .cover-image {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        """
        css_path = os.path.join(self.output_dir, 'style.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        return 'style.css'

    def _create_navigation(self, current_index, total_chapters):
        """Create navigation links"""
        prev_link = f'chapter_{current_index-1:03d}.html' if current_index > 1 else 'index.html'
        next_link = f'chapter_{current_index+1:03d}.html' if current_index < total_chapters else 'index.html'
        
        nav_html = f'''
        <div class="navigation">
            <a href="{prev_link}" class="nav-button">← Previous</a>
            <a href="index.html" class="nav-button">Table of Contents</a>
            <a href="{next_link}" class="nav-button">Next →</a>
        </div>
        '''
        return nav_html

    def _extract_cover(self):
        """Extract cover image from EPUB"""
        try:
            for item in self.book.get_items():
                if isinstance(item, epub.EpubCover) or item.get_name().lower().endswith(('cover.jpg', 'cover.jpeg', 'cover.png')):
                    cover_path = os.path.join('images', 'cover' + os.path.splitext(item.get_name())[1])
                    full_path = os.path.join(self.output_dir, cover_path)
                    with open(full_path, 'wb') as f:
                        f.write(item.get_content())
                    logger.info(f"Extracted cover image: {cover_path}")
                    return cover_path
        except Exception as e:
            logger.error(f"Error extracting cover: {str(e)}")
        return None

    def _create_toc(self, chapters, cover_path=None):
        """Create table of contents page"""
        toc_html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Table of Contents</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <div class="toc">
        '''
        
        if cover_path:
            toc_html += f'''
                <div class="cover">
                    <img src="{cover_path}" alt="Book Cover" class="cover-image">
                </div>
            '''
        
        toc_html += '''
                <h1>Table of Contents</h1>
                <ul class="toc-list">
        '''
        
        for idx, (title, _) in enumerate(chapters, 1):
            clean_title = title if title else f"Chapter {idx}"
            toc_html += f'<li><a href="chapter_{idx:03d}.html">{clean_title}</a></li>\n'
        
        toc_html += '''
                </ul>
            </div>
        </body>
        </html>
        '''
        
        with open(os.path.join(self.output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(toc_html)

    def _extract_title(self, soup):
        """Extract title from HTML content"""
        # Try different heading tags
        for tag in ['h1', 'h2', 'title']:
            title_tag = soup.find(tag)
            if title_tag:
                return title_tag.get_text(strip=True)
        return None

    def convert(self):
        """
        Convert EPUB to HTML files
        
        :return: List of generated HTML file paths
        """
        logger.info(f"Starting conversion of {self.epub_path}")
        
        try:
            # Read the EPUB file
            self.book = epub.read_epub(self.epub_path)
            logger.info("Successfully loaded EPUB file")
            
            # Extract and save images
            self._save_images()
            
            # Extract cover
            cover_path = self._extract_cover()
            
            # Create stylesheet
            css_file = self._create_stylesheet()
            logger.info("Created stylesheet")
            
            # Store generated HTML file paths
            generated_files = []
            chapters = []
            
            # Get all items
            items = list(self.book.get_items())
            logger.info(f"Found {len(items)} items in EPUB")
            
            # Process document items
            document_items = [item for item in items if item.get_type() == ebooklib.ITEM_DOCUMENT]
            total_chapters = len(document_items)
            
            # Counter for chapters
            chapter_count = 0
            
            # Process each item
            for item in document_items:
                try:
                    chapter_count += 1
                    logger.info(f"Processing chapter {chapter_count}")
                    
                    # Extract content
                    content = item.get_content().decode('utf-8')
                    
                    # Process images in content
                    content = self._process_images_in_content(content)
                    
                    # Parse with BeautifulSoup for clean HTML
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract title
                    chapter_title = self._extract_title(soup)
                    chapters.append((chapter_title, chapter_count))
                    
                    # Add basic HTML structure if missing
                    if not soup.find('html'):
                        new_html = BeautifulSoup('<!DOCTYPE html><html><head></head><body></body></html>', 'html.parser')
                        new_html.body.append(soup)
                        soup = new_html
                    
                    # Add stylesheet link
                    if not soup.find('link', {'href': css_file}):
                        css_link = soup.new_tag('link', href=css_file, rel='stylesheet', type='text/css')
                        soup.head.append(css_link)
                    
                    # Add viewport meta tag
                    if not soup.find('meta', {'name': 'viewport'}):
                        meta = soup.new_tag('meta', content='width=device-width, initial-scale=1.0')
                        meta['name'] = 'viewport'
                        soup.head.append(meta)
                    
                    # Add title if missing
                    if not soup.title:
                        title = soup.new_tag('title')
                        title.string = chapter_title if chapter_title else f"Chapter {chapter_count}"
                        soup.head.append(title)
                    
                    # Wrap content in chapter-content div
                    if soup.body:
                        content_div = soup.new_tag('div')
                        content_div['class'] = 'chapter-content'
                        for tag in list(soup.body.children):
                            content_div.append(tag)
                        soup.body.clear()
                        soup.body.append(content_div)
                    
                    # Add navigation
                    nav_html = self._create_navigation(chapter_count, total_chapters)
                    nav_soup = BeautifulSoup(nav_html, 'html.parser')
                    if soup.body:
                        soup.body.insert(0, nav_soup)
                        soup.body.append(nav_soup)
                    
                    # Generate filename
                    filename = f"chapter_{chapter_count:03d}.html"
                    file_path = os.path.join(self.output_dir, filename)
                    
                    # Write clean HTML with proper encoding declaration
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(soup.prettify()))
                    
                    logger.info(f"Created HTML file: {filename}")
                    generated_files.append(file_path)
                    
                except Exception as e:
                    logger.error(f"Error processing chapter {chapter_count}: {str(e)}")
                    continue
            
            # Create table of contents with cover
            self._create_toc(chapters, cover_path)
            logger.info("Created table of contents")
            
            logger.info(f"Conversion complete. Generated {len(generated_files)} HTML files")
            return generated_files
            
        except Exception as e:
            logger.error(f"Error converting EPUB: {str(e)}")
            raise

    def get_book_metadata(self):
        """
        Extract book metadata
        
        :return: Dictionary of book metadata
        """
        metadata = {}
        if self.book:
            metadata['title'] = self.book.get_metadata('DC', 'title')[0][0] if self.book.get_metadata('DC', 'title') else 'Unknown Title'
            metadata['creator'] = self.book.get_metadata('DC', 'creator')[0][0] if self.book.get_metadata('DC', 'creator') else 'Unknown Author'
            logger.info(f"Extracted metadata - Title: {metadata['title']}, Creator: {metadata['creator']}")
        return metadata

def main():
    import sys
    
    # Check if EPUB path is provided
    if len(sys.argv) < 2:
        logger.error("No EPUB file specified")
        print("Usage: python epub_to_html_converter.py <path_to_epub>")
        sys.exit(1)
    
    epub_path = sys.argv[1]
    
    # Create converter
    try:
        converter = EPUBToHTMLConverter(epub_path)
        
        # Convert EPUB
        html_files = converter.convert()
        
        # Print metadata and generated files
        metadata = converter.get_book_metadata()
        print(f"Converted Book: {metadata['title']} by {metadata['creator']}")
        print("\nGenerated HTML Files:")
        print(" - index.html (Table of Contents)")
        print(" - style.css (Stylesheet)")
        for file in html_files:
            print(f" - {os.path.basename(file)}")
        
        if not html_files:
            print("\nWarning: No HTML files were generated. This might indicate an issue with the EPUB file structure.")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
