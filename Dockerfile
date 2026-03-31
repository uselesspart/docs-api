FROM python:3.12

WORKDIR /app
COPY ./main.py /app
COPY ./requirements.txt /app
COPY ./contract_template.docx /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]