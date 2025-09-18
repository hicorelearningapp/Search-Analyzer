# import os
# from config import Config
# <<<<<<< HEAD
# from .llm_summarizer import LLMSummarizer
# =======
# from docx import Document
# >>>>>>> 90f66b0688eb50c8ddb3741139e31ee1273e1edb

# class SummarizerPipeline:
#     def __init__(self):
#         pass

# <<<<<<< HEAD
#         if llm:
#             self.summarizer = llm
#         else:
#             self.summarizer = LLMSummarizer()
# =======
#     def run(self, text: str, doc_type: str, pages: int, label: str, outfile_name: str, download: bool = False):
#         try:
#             # Generate document (example with python-docx)
#             document = Document()
#             document.add_heading(doc_type, 0)
#             document.add_paragraph(f"Topic: {label}")
#             document.add_paragraph(text)
# >>>>>>> 90f66b0688eb50c8ddb3741139e31ee1273e1edb

#             # Always save file to /reports
#             if not os.path.exists(Config.REPORTS_DIR):
#                 os.makedirs(Config.REPORTS_DIR)

# <<<<<<< HEAD
#     def run(self, text: str, doc_type: str, pages: int, label: str, outfile_name: str, download: bool = False) -> Dict[str, Any]:
#         summary = self.summarizer.summarize_with_structure(text, doc_type=doc_type, pages=pages)
#         safe_name = "".join(c if c.isalnum() else "_" for c in outfile_name)[:200]
#         outfile = os.path.join(self.reports_dir, f"{safe_name}_{doc_type}.docx")
#         path = self.generator.generate_docx(
#             content={"content": summary["content"]}, 
#             output_path=outfile, 
#             doc_type=doc_type, 
#             title=label
#         )
#         if download:
#             return FileResponse(path, filename=os.path.basename(path))
#         return {
#             "summary": summary["content"],
#             "docx": path,
#             "cached": summary.get("cached", False),
#             "headings": summary.get("headings"),
#             "model": summary.get("model"),
#         }
# =======
#             outfile_path = os.path.join(Config.REPORTS_DIR, f"{outfile_name}.docx")
#             document.save(outfile_path)

#             # If download requested, return a public link
#             if download:
#                 return {
#                     "status": "success",
#                     "file_url": f"/reports/{outfile_name}.docx"
#                 }

#             # Otherwise return inline summary only
#             return {
#                 "status": "success",
#                 "summary": text,
#                 "doc_type": doc_type,
#                 "pages": pages,
#                 "label": label
#             }

#         except Exception as e:
#             return {"status": "error", "message": str(e)}
# >>>>>>> 90f66b0688eb50c8ddb3741139e31ee1273e1edb
