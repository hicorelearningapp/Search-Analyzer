# sources/pdf_loader.py
import os
import fitz
from unstructured.partition.auto import partition
import pytesseract
from PIL import Image
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from fastapi import UploadFile, Form
from datetime import datetime
from fastapi.responses import JSONResponse


class PDFExtractor:

    def __init__(self):
        pass

    def extract_text(self, file_path: str) -> str:
        elements = partition(filename=file_path)
        text = "\n".join([el.text for el in elements if getattr(el, "text", None)])

        doc = fitz.open(file_path)
        for i, page in enumerate(doc):
            for j, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix0 = fitz.Pixmap(fitz.csGRAY, pix)
                else:
                    pix0 = pix
                img_path = f"temp_{i}_{j}.png"
                pix0.save(img_path)
                try:
                    text += "\n" + pytesseract.image_to_string(Image.open(img_path))
                finally:
                    os.remove(img_path)
        return text


class TextIndexer:

    def __init__(self, embed_model_name: str = "all-MiniLM-L6-v2"):
        self.embed_model = SentenceTransformer(embed_model_name)
        self.text_chunks = []
        self.faiss_index = None

    def build_index(self, text: str, chunk_size: int = 500):
        self.text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        if not self.text_chunks:
            self.faiss_index = None
            return

        embeddings = self.embed_model.encode(self.text_chunks, show_progress_bar=False)
        dim = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dim)
        self.faiss_index.add(np.array(embeddings).astype("float32"))

    def search(self, query: str, top_k: int = 3) -> list:
        if self.faiss_index is None or not self.text_chunks:
            return []

        q_emb = self.embed_model.encode([query]).astype("float32")
        distances, indices = self.faiss_index.search(np.array(q_emb), top_k)
        idxs = indices[0].tolist()
        return [self.text_chunks[i] for i in idxs if i is not None and 0 <= i < len(self.text_chunks)]


class PDFSummarizer:
    
    def __init__(self, reports_dir: str = None):
        self.extractor = PDFExtractor()
        self.indexer = TextIndexer()
        self.reports_dir = reports_dir or os.path.join(os.getcwd(), "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    async def summarize_pdf(
        self,
        file: UploadFile,
        doc_type: str = Form(...),
        pages: int = Form(2),
        download: bool = Form(False)
    ):
        from summarizer.common import SummarizerPipeline

        # Create a temporary file path
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        
        try:
            # Save file to temporary location
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Extract text (file will be closed automatically after this block)
            text = self.extractor.extract_text(file_path)
            
            # Build index
            self.indexer.build_index(text)
            
            # Initialize and run summarizer pipeline
            pipeline = SummarizerPipeline()
            result = pipeline.run(
                text=text,
                doc_type=doc_type,
                pages=pages,
                label=file.filename,
                outfile_name=os.path.splitext(file.filename)[0],
                download=download
            )
            
            # Ensure we close the uploaded file
            await file.close()
            return result
            
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})
            
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Failed to clean up temporary directory: {e}")
