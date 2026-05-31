import fitz #pymupdf
import requests
from langchain.tools import tool

@tool
def pdf_reader(source: str)-> str:
    '''
    Read and extract Text from pdf file
    Source can be a URL(https://....) or a local file path (C:path/to/file.pdf)
    Use this when the user wants to read summarize , or extract information from PDF.
    '''
    print(f"[Tool call pdf reader] for source: {source}")
    
    try:
        if source.startswith("http://") or source.startswith("https://"):
            response = requests.get(source, timeout=10)
            if response.status_code != 200:
                return f"Failed to download PDF. Stauts code{response.status_code}"
        
            pdf_bytes= response.content
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        else:
            doc = fitz.open(source)
            
        text = ""
        
        for page_num, page in enumerate(doc):
            text += f"\n ---Page {page_num+1}---\n"
            text += page.get_text()

        doc.close()
        
        if len(text) > 8000:
            text = text[:8000] + "\n\n [Content Truncated...]"
            
        return text if text.strip() else "No text could be extracted from pdf."
    
    except FileNotFoundError:
        return f"File not found: {source}"
    except Exception as e:
        return f"PDF reading error: {str(e)}"