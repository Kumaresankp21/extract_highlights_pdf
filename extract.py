import fitz  # PyMuPDF

def extract_highlighted_paragraphs_with_pages(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    paragraphs = []

    # Iterate through pages
    for page_num in range(len(doc)):
        page = doc[page_num]
        annotations = page.annots()

        # Check if there are any annotations (highlights)
        if annotations:
            for annot in annotations:
                if annot.type[0] == 8:  # Check if the annotation is a highlight (8)
                    try:
                        # Use vertices to define the area of the highlight
                        vertices = annot.vertices
                        if vertices:
                            # Determine the minimum and maximum x and y coordinates
                            x_min = min(vertices, key=lambda v: v[0])[0]
                            y_min = min(vertices, key=lambda v: v[1])[1]
                            x_max = max(vertices, key=lambda v: v[0])[0]
                            y_max = max(vertices, key=lambda v: v[1])[1]
                            rect = fitz.Rect(x_min, y_min, x_max, y_max)

                            # Extract the full paragraph containing the highlighted text
                            block_list = page.get_text("blocks")
                            
                            for block in block_list:
                                b = fitz.Rect(block[:4])
                                if b.intersects(rect):
                                    paragraphs.append((page_num + 1, block[4].strip()))

                    except Exception as e:
                        print(f"Error processing annotation on page {page_num + 1}: {e}")

    doc.close()
    return paragraphs

