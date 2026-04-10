import zipfile
import xml.etree.ElementTree as ET
import os

def extract_text_from_pptx(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    try:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            # PPTX is a zip of XML files. Slides are in ppt/slides/
            slide_files = [f for f in zip_ref.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            slide_files.sort() # Sort slides in order

            full_text = []
            for slide_file in slide_files:
                with zip_ref.open(slide_file) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    # Namespaces for PPTX
                    ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
                          'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}
                    
                    # Find all text elements
                    slide_text = []
                    for t in root.findall('.//a:t', ns):
                        if t.text:
                            slide_text.append(t.text)
                    
                    if slide_text:
                        full_text.append(f"--- Slide {slide_file} ---\n" + "\n".join(slide_text))
            
            return "\n\n".join(full_text)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    ppt_path = r"e:\AI Dect\Android_Malware_Detection.pptx"
    content = extract_text_from_pptx(ppt_path)
    if content:
        with open("ppt_content.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print("Successfully extracted content to ppt_content.txt")
    else:
        print("Failed to extract content.")
