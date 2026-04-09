import uuid
from fastapi import FastAPI, HTTPException, status
from docx import Document
from docx.shared import Pt
from datetime import datetime

from s3_client import S3Client

ru_months = {
    "January" : "января",
    "February" : "февраля",
    "March" : "марта",
    "April" : "апреля",
    "May" : "мая",
    "June" : "июня",
    "July" : "июля",
    "August" : "августа",
    "September" : "сентября",
    "October" : "октября",
    "November" : "ноября",
    "December" : "декабря"
}

def normalize_text(p):
    for run in p.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

app = FastAPI()
items = []
items_id = 1

@app.get('/')
def root():
    return {'message': 'Hello World!'}

@app.post('/generate_docs/')
def generate_docs(
        customer_inn:str,
        customer_ogrn:str,
        customer_org_name:str,
        tour_price,
        tour_date,
        contract_date:datetime,
        tour_cost):
    template = Document('contract_template.docx')
    unique_id = uuid.uuid4().int
    short_uniue_id = str(unique_id)[:8]

    #Date parsing
    if contract_date:
        contract_day = contract_date.day
        contract_month = contract_date.strftime("%B")
        contract_month_ru = ru_months[contract_month]
        contract_year = contract_date.year
        for p in template.paragraphs:
            if 'contract_date' in p.text:
                p.text = p.text.replace('contract_date', f'«{contract_day}» {contract_month_ru} {contract_year}г.')
                normalize_text(p=p)
            if 'contract_uuid' in p.text:
                p.text = p.text.replace('contract_uuid', f'{short_uniue_id}')
                normalize_text(p=p)
            if 'customer_org_name' in p.text:
                p.text = p.text.replace('customer_org_name', customer_org_name)
                normalize_text(p=p)
    
    for table in template.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                            if 'customer_org_name' in run.text:
                                run.text = run.text.replace('customer_org_name', customer_org_name)
                            if 'customer_ogrn' in run.text:
                                run.text = run.text.replace('customer_ogrn', f'ОГРН {customer_ogrn}')
                            if 'customer_inn' in run.text:
                                run.text = run.text.replace('customer_inn', f'ИНН {customer_inn}')
                            run.font.name = "Times New Roman"
                            run.font.size = Pt(12)
    template.save('result.docx')
    s3_client = S3Client()
    with open('result.docx', "rb") as f:
        result = s3_client.upload_file(
            file_content=f.read(),
            filename=f"{unique_id}_contract.docx",
            folder="test_folder"
        )
    return(result)
