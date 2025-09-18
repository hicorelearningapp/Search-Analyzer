import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from sources.pdf_loader import PDFManager
from sources.retriever import RetrievalMethod

app = FastAPI()

# Initialize the PDF manager with FAISS retriever
pdf_manager = PDFManager(
    chunk_size=1000,
    chunk_overlap=150,
    retrieval_method=RetrievalMethod.FAISS,
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

async def process_pdf(file_path: str):
    """Process a PDF file and return the PDFManager instance."""
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Create a mock UploadFile from the file path
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    upload_file = UploadFile(
        filename=Path(file_path).name,
        file=io.BytesIO(file_content)
    )
    
    # Process the PDF
    text = await pdf_manager.get_text_from_pdf(upload_file)
    print(f"Processed PDF with {len(text)} characters")
    return pdf_manager

async def interactive_qa(pdf_manager):
    """Interactive question-answering loop."""
    print("\nEnter your questions about the document (type 'exit' to quit):")
    while True:
        query = input("\nQuestion: ").strip()
        if query.lower() in ['exit', 'quit', 'q']:
            break
            
        try:
            # Get relevant document chunks
            results = pdf_manager.search_documents(query, k=3)
            
            if not results:
                print("No relevant information found.")
                continue
                
            print("\nRelevant information:")
            for i, chunk in enumerate(results, 1):
                print(f"\n--- Chunk {i} ---")
                print(chunk[:500] + ("..." if len(chunk) > 500 else ""))
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    import sys
    import io
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_qa_example.py <path_to_pdf>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    
    try:
        # Process the PDF
        pdf_manager = asyncio.run(process_pdf(pdf_path))
        
        # Start interactive Q&A
        asyncio.run(interactive_qa(pdf_manager))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
