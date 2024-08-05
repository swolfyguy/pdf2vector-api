import PyPDF2


def extract_text_from_pdf(pdf_path):
    texts = []
    print(pdf_path)
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            texts.append(reader.pages[page].extract_text())
    return texts
