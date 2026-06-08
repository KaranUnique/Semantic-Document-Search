import os
import hashlib
import logging
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
from pptx import Presentation as PptxPresentation

logger = logging.getLogger("doc_processor")
logging.basicConfig(level=logging.INFO)


class RecursiveCharacterTextSplitter:
    """
    Lightweight custom text splitter.
    Splits text into chunks while respecting natural boundaries,
    with proper overlapping between consecutive chunks.
    """
    def __init__(self, chunk_size=1000, chunk_overlap=200, length_function=len):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function

    def split_text(self, text):
        if not text:
            return []
        if self.length_function(text) <= self.chunk_size:
            return [text]

        separators = ["\n\n", "\n", ". ", " "]
        raw_splits = []
        for separator in separators:
            parts = text.split(separator)
            if len(parts) > 1:
                if separator not in (" ", ""):
                    raw_splits = [p + separator for p in parts[:-1]] + [parts[-1]]
                else:
                    raw_splits = parts
                break

        if not raw_splits:
            raw_splits = [text]

        base_chunks = []
        current = ""
        for split in raw_splits:
            if not split.strip():
                continue
            if self.length_function(current) + self.length_function(split) <= self.chunk_size:
                current += split
            else:
                if current.strip():
                    base_chunks.append(current.strip())
                if self.length_function(split) > self.chunk_size:
                    base_chunks.extend(self.split_text(split))
                    current = ""
                else:
                    current = split

        if current.strip():
            base_chunks.append(current.strip())

        if not base_chunks:
            return [text]

        if self.chunk_overlap <= 0 or len(base_chunks) <= 1:
            return base_chunks

        # Build overlapped chunks: each chunk starts with the tail of the previous one
        overlapped = [base_chunks[0]]
        for i in range(1, len(base_chunks)):
            prev = base_chunks[i - 1]
            overlap_prefix = prev[-self.chunk_overlap:].strip()
            new_chunk = (overlap_prefix + " " + base_chunks[i]).strip()
            overlapped.append(new_chunk)

        return [c for c in overlapped if c]




class DocProcessor:
    def __init__(self, upload_dir="./uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    @staticmethod
    def calculate_md5(file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def process_file(self, file_path, filename):
        file_ext = os.path.splitext(filename)[1].lower()
        chunks = []
        page_count = 0

        try:
            if file_ext == ".pdf":
                pages_text, page_count = self._extract_pdf(file_path)
            elif file_ext == ".docx":
                pages_text, page_count = self._extract_docx(file_path)
            elif file_ext == ".pptx":
                pages_text, page_count = self._extract_pptx(file_path)
            elif file_ext in (".txt", ".md"):
                pages_text, page_count = self._extract_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

            for page_idx, text in pages_text.items():
                cleaned_text = self._clean_text(text)
                if not cleaned_text:
                    continue
                sub_chunks = self.text_splitter.split_text(cleaned_text)
                for chunk_idx, chunk_text in enumerate(sub_chunks):
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "source": filename,
                            "page": page_idx,
                            "chunk_index": chunk_idx,
                            "file_type": file_ext
                        }
                    })

            logger.info(f"Processed '{filename}': {page_count} pages, {len(chunks)} chunks.")
            return chunks, page_count

        except Exception as e:
            logger.error(f"Error processing file '{filename}': {str(e)}")
            raise

    def _clean_text(self, text):
        if not text:
            return ""
        lines = [line.strip() for line in text.splitlines()]
        return " ".join(line for line in lines if line)

    def _extract_pdf(self, file_path):
        pages_text = {}
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        for idx, page in enumerate(reader.pages):
            pages_text[idx + 1] = page.extract_text() or ""
        return pages_text, total_pages

    def _extract_docx(self, file_path):
        pages_text = {}
        doc = DocxDocument(file_path)
        current_page = 1
        char_count = 0
        page_content = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            page_content.append(text)
            char_count += len(text)
            if char_count > 2000:
                pages_text[current_page] = "\n".join(page_content)
                current_page += 1
                char_count = 0
                page_content = []

        if page_content or not pages_text:
            pages_text[current_page] = "\n".join(page_content)

        return pages_text, len(pages_text)

    def _extract_pptx(self, file_path):
        pages_text = {}
        prs = PptxPresentation(file_path)
        for idx, slide in enumerate(prs.slides):
            slide_text = [
                shape.text.strip()
                for shape in slide.shapes
                if hasattr(shape, "text") and shape.text.strip()
            ]
            pages_text[idx + 1] = "\n".join(slide_text)
        return pages_text, len(prs.slides)

    def _extract_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return {1: content}, 1