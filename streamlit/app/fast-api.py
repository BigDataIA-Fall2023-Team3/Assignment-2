from fastapi import FastAPI
from pydantic import BaseModel
from main import download_pdf, pypdf_extract, get_answers

app = FastAPI()

class PDFRequest(BaseModel):
    pdf_url: str

class QuestionRequest(BaseModel):
    pdf_text: str
    question: str

@app.post("/upload-pdf/")
async def upload_pdf(request: PDFRequest):
    try:
        pdf_url = request.pdf_url
        # Call your existing code to download and process the PDF
        result = pypdf_extract(pdf_url)  # Replace with your PDF processing code
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/ask-question/")
async def ask_question(request: QuestionRequest):
    try:
        pdf_text = request.pdf_text
        question = request.question
        # Call your existing code to answer the question based on the provided text
        answer = get_answers(pdf_text, question)  # Replace with your question-answering code
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)}
