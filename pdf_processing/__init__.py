from pdf_processing.extract_text import extract_text_from_pdf
from pdf_processing.generate_embeddings import generate_embeddings
from pdf_processing.store_embeddings import store_embeddings_in_chroma

def process_pdf_and_store(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    embeddings = generate_embeddings(text)
    store_embeddings_in_chroma(embeddings, text)
    print("Embeddings stored successfully.")

# Example Usage
if __name__ == "__main__":
    process_pdf_and_store("path_to_your_pdf_file.pdf")
