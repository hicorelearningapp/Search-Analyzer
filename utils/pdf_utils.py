import os, tempfile
from .http_utils import safe_request_get

try:
    import pdfplumber
except:
    pdfplumber = None

def download_pdf_to_text(url: str) -> str:
    if not url:
        return ""
    try:
        r = safe_request_get(url, timeout=30)
        if not r or r.status_code != 200:
            return ""
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(r.content)
        tmp.flush()
        tmp_path = tmp.name
        tmp.close()

        text = ""
        if pdfplumber:
            try:
                with pdfplumber.open(tmp_path) as pdf:
                    for p in pdf.pages:
                        t = p.extract_text()
                        if t:
                            text += t + "\n"
            except Exception:
                pass

        if not text:
            try:
                import fitz
                with fitz.open(tmp_path) as doc:
                    for page in doc:
                        text += page.get_text()
            except Exception:
                pass

        os.unlink(tmp_path)
        return text or ""
    except Exception as e:
        print("download_pdf_to_text failed:", e)
        return ""
