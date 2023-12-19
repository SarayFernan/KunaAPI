from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
import models

app = FastAPI()

# TODO response_model te obliga a devolver eso en concreto, cambiar los métodos que no sea necesario

# Conectar a la base de datos MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.kuna_db
#collection_pets = db.pets_collection
collection_posts = db.posts_collection
collection_users = db.users_collection
#collection_coments = db.coments_collection

@app.get("/health")
def read_root():
    return {"mensaje": "Im alive"}

# Leer un recurso por su ID TODO cambiar a buscar con filtros
@app.get('/posts/{id}', response_model=models.Post)
async def read_mascota(id: str):
    pet = await collection_posts.find_one({"id": id})
    if pet is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    return pet

# Pedir posts más recientes
@app.get('/posts', response_model=list[models.Post])
async def read_posts():
    # Ordena por fecha de publicación en orden descendente y limita a 20 resultados
    posts = await collection_posts.find().sort("date", -1).limit(20).to_list(None)
    # Carga el usuario para cada post
    # for p in posts:
    #     p["user"] = await collection_users.find_one({"id": p["user"]})
    return posts

# Crear un nuevo post
@app.post('/posts', response_model=models.Post)
async def create_post(post: models.Post):
    post_dict = post.model_dump()
    result = await collection_posts.insert_one(post_dict)
    post_dict['id'] = str(result.inserted_id)
    return post

# Eliminar un post por su ID
@app.delete('/posts/{id}')
async def delete_post(id: str):
    post = await collection_posts.find_one({"id": id})
    if post is None:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    await collection_posts.delete_one({"id": id})
    return {"mensaje": "Post eliminada"}

# autenticar usuario
@app.post('/authenticate')
async def authenticate(user: models.User):
    user_dict = user.model_dump()
    result = await collection_users.find_one({"name": user_dict["name"], "password": user_dict["password"]})
    return result is not None

# Crear una nuevo usuario
@app.post('/users', response_model=models.User)
async def create_user(user: models.User):
    user_dict = user.model_dump()
    result = await collection_users.insert_one(user_dict)
    user_dict['id'] = str(result.inserted_id)
    return user

# Eliminar una usuario por su ID
@app.delete('/users/{id}', response_model=dict)
async def delete_pet(id: str):
    user = await collection_users.find_one({"id": id})
    if user is None:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    await collection_users.delete_one({"id": id})
    return {"mensaje": "Usuario eliminado"}

#En este paso, verificamos si el script está siendo ejecutado directamente y, en ese caso, iniciamos el servidor FastAPI en el puerto 8000.  
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)



    
