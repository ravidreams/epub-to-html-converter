# EPUB to HTML Converter

A Python tool that converts EPUB files into a collection of well-organized, styled HTML files with navigation and table of contents.

## Features

- Convert EPUB books to clean, readable HTML files
- Automatically generate table of contents
- Modern, responsive design with CSS styling
- Chapter-to-chapter navigation
- Mobile-friendly layout
- Preserves book structure and content
- Extracts and displays book metadata

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/epub-to-html-converter.git
   cd epub-to-html-converter
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Convert an EPUB file to HTML:
```bash
python epub_to_html_converter.py path/to/your/book.epub
```

This will:
1. Create a new directory named `[book-name]_html`
2. Generate individual HTML files for each chapter
3. Create a table of contents (`index.html`)
4. Add a stylesheet (`style.css`)
5. Add navigation between chapters

## Output Structure

```
book_name_html/
├── index.html          # Table of contents
├── style.css          # Stylesheet
├── chapter_001.html   # First chapter
├── chapter_002.html   # Second chapter
└── ...                # Additional chapters
```

## Features in Detail

### Table of Contents
- Automatically generated from chapter titles
- Clean, modern design
- Easy navigation to any chapter

### Styling
- Responsive layout
- Clean typography
- Proper spacing and margins
- Light color scheme for better readability
- Mobile-friendly design

### Navigation
- Previous/Next chapter buttons
- Quick access to table of contents
- Visual feedback on hover
- Consistent navigation bar at top and bottom

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Uses `ebooklib` for EPUB parsing
- Uses `beautifulsoup4` for HTML processing
