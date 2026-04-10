import zipfile
import xml.etree.ElementTree as ET
import sys

def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = ET.fromstring(xml_content)

    paragraphs = []
    # Namespaces
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    for paragraph in tree.findall('.//w:p', ns):
        texts = [node.text for node in paragraph.findall('.//w:t', ns) if node.text]
        if texts:
            paragraphs.append("".join(texts))

    return "\n".join(paragraphs)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_docx.py <path>")
        sys.exit(1)
    
    try:
        text = get_docx_text(sys.argv[1])
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Successfully extracted to {sys.argv[2]}")
    except Exception as e:
        print(f"Error: {e}")
