from fastapi.responses import RedirectResponse
from langserve import add_routes
from RAG import *
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
import shutil
import json
import os

app = FastAPI(    title="Chain-Server",
    version="0.1",
    description="Langchain based RAG API")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)



@app.get("/docs")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")
 


@app.post("/debugging")
async def call_make_check():
    check_working()

@app.post("/chat")
async def chat(request: Request):
    #print("Headers:", request.headers)
    body = await request.json()
    #print("Body:", body)
    try:
        result = get_answer(body)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/index-file/")
async def index_file(file: UploadFile = File(...), access: str = Form(...), metadata: str = Form(...)):
    try:
        # Define a path to save the file temporarily
        temp_file_path = f"temp/{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        metadata_dict = json.loads(metadata)
        indexing_file(temp_file_path, access, metadata_dict)
        
        # Optionally, delete the temp file after indexing if no longer needed
        os.remove(temp_file_path)
        
        return JSONResponse(content={"message": "File indexed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
        

@app.post("/index-formation/")
async def index_formation(formation_data: str = Form(...), syllabus_pdf: Optional[UploadFile] = File(None)):
    try:
        # Charger les données de la formation
        formation_data = json.loads(formation_data)
        
        # Construire le texte à indexer
        texte_formation = (
            f"La formation {formation_data['nom']} ouvrira le {formation_data['date']} "
            f"pour un maximum de {formation_data['nombre_personnes']} personnes avec des frais "
            f"d'inscription de {formation_data['frais_inscription']}. Elle prépare au diplôme "
            f"{formation_data['diplome']} qui permet d'exercer le métier de {formation_data['metier']}. "
            f"Voici la liste des pré-requis : {formation_data['pre_requis']}."
        )
        
        # Ajouter le syllabus_pdf si disponible
        temp_file_path = None
        if syllabus_pdf:
            temp_file_path = f"temp/{syllabus_pdf.filename}"
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(syllabus_pdf.file, buffer)
        
        metadata = {
            'nom': formation_data['nom'],
            'date': formation_data['date'],
            'nombre_personnes': formation_data['nombre_personnes'],
            'frais_inscription': formation_data['frais_inscription'],
            'pre_requis': formation_data['pre_requis'],
            'diplome': formation_data['diplome'],
            'metier': formation_data['metier'],
            'date_upload': formation_data['date_upload'],
        }
        
        indexing_formation(temp_file_path,texte_formation, metadata)
        
        if temp_file_path is not None :
            # Optionally, delete the temp file after indexing if no longer needed
            os.remove(temp_file_path)
        
        return JSONResponse(content={"message": "Formation indexed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.post("/deindex-file/")
async def deindex_file(name: str = Form(...), access: str = Form(...)):
    try:
        deindexing_file(name,access)
        
        return JSONResponse(content={"message": "Document deindexed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
        
@app.post("/deindex-formation/")
async def deindex_formation(name: str = Form(...), access: str = Form(...)):
    try:
        deindexing_formation(name,access)
        
        return JSONResponse(content={"message": "Document deindexed successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
    

