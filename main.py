from fastapi import FastAPI, HTTPException, status

app = FastAPI()
items = []
items_id = 1

@app.get('/')
def root():
    return {'message': 'Hello World'}

@app.post('/generate_docs/')
def generate_docs(
    tour_agent_inn,
    tour_agent_ogrn,
    tour_agent_org_name,
    tour_agent_price,
    tour_agent_date):
    pass