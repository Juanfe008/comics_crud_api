from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from sqlalchemy.sql import select
from databases import Database
from fastapi.middleware.cors import CORSMiddleware

# Configuración de la base de datos
DATABASE_URL = "postgresql://comics_crud_owner:BwOMTkgvn8x4@ep-fragrant-forest-a4ecw7r8.us-east-1.aws.neon.tech/comics_crud?sslmode=require"  # Actualiza esto con tu conexión real
database = Database(DATABASE_URL)
metadata = MetaData()

# Definición de la tabla 'comics'
comics = Table(
    "comics",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255)),
    Column("description", String(255)),
    Column("author", String(255)),
    Column("price", Float),
    Column("stock", Integer),
)

# Creación del motor de la base de datos
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# Inicialización de la aplicación FastAPI
app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eventos de conexión/desconexión a la base de datos
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Rutas de la API
@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/comics")
async def read_comics():
    query = comics.select()
    return await database.fetch_all(query)

@app.get("/comics/{comic_id}")
async def read_comic(comic_id: int):
    query = comics.select().where(comics.c.id == comic_id)
    comic = await database.fetch_one(query)
    if comic is None:
        raise HTTPException(status_code=404, detail="Comic not found")
    return comic

@app.post("/comics")
async def create_comic(comic: dict):
    query = comics.insert().values(
        title=comic["title"],
        description=comic["description"],
        author=comic["author"],
        price=comic["price"],
        stock=comic["stock"],
    )
    comic_id = await database.execute(query)
    return {**comic, "id": comic_id}

@app.put("/comics/{comic_id}")
async def update_comic(comic_id: int, comic: dict):
    query = comics.update().where(comics.c.id == comic_id).values(
        title=comic["title"],
        description=comic["description"],
        author=comic["author"],
        price=comic["price"],
        stock=comic["stock"],
    )
    result = await database.execute(query)
    if not result:
        raise HTTPException(status_code=404, detail="Comic not found")
    return {**comic, "id": comic_id}

@app.delete("/comics/{comic_id}")
async def delete_comic(comic_id: int):
    query = comics.delete().where(comics.c.id == comic_id)
    result = await database.execute(query)
    if not result:
        raise HTTPException(status_code=404, detail="Comic not found")
    return {"message": "Comic deleted successfully"}
