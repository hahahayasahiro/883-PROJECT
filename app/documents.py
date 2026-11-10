"""Transient text extraction. Uploaded originals are never stored on disk."""
import io
from pathlib import Path
from fastapi import HTTPException
from pypdf import PdfReader

MAX_SIZE=5*1024*1024
MAX_TEXT=60000

def extract(data:bytes,name:str):
    safe_name=Path(name.replace('\\','/')).name[:250]
    if not data:raise HTTPException(422,'The file is empty.')
    if len(data)>MAX_SIZE:raise HTTPException(413,'Maximum upload size is 5 MB.')
    suffix=Path(safe_name).suffix.lower()
    if suffix=='.txt':
        try:text=data.decode('utf-8-sig')
        except UnicodeDecodeError:raise HTTPException(422,'Use a UTF-8 text file.')
        if '\x00' in text:raise HTTPException(422,'The file is not valid plain text.')
        pages=1
    elif suffix=='.pdf':
        if not data.startswith(b'%PDF-'):raise HTTPException(422,'The file is not a valid PDF.')
        try:
            reader=PdfReader(io.BytesIO(data))
            if reader.is_encrypted:raise HTTPException(422,'Encrypted PDFs are not supported.')
            pages=len(reader.pages)
            if pages>20:raise HTTPException(422,'PDFs must have at most 20 pages.')
            parts=[p.extract_text() or '' for p in reader.pages]
            if any(not p.strip() for p in parts):raise HTTPException(422,'A PDF page has no extractable text. Scanned or mixed-image documents require OCR and are not supported.')
            text='\n\n'.join(parts)
        except HTTPException:raise
        except Exception:raise HTTPException(422,'The PDF could not be read. Use a text-based PDF or TXT.')
    else:raise HTTPException(422,'Only TXT and text-based PDF files are supported.')
    if not text.strip():raise HTTPException(422,'No text could be extracted.')
    if len(text)>MAX_TEXT:raise HTTPException(422,'Extracted text exceeds 60,000 characters. Upload a shorter document.')
    return {'file_name':safe_name,'text':text.strip(),'pages':pages,'characters':len(text),'notice':'Text extracted locally. AI is called only when you request extraction suggestions or pre-review.'}
