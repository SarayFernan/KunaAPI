from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
import models

# Crear una instancia de la aplicación FastAPI
app = FastAPI()



# Conectar a la base de datos MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.kuna_db

# Colecciones en la base de datos
collection_posts = db.posts_collection
collection_users = db.users_collection
collection_user_accounts = db.users_account_collection


# Pedir posts más recientes
@app.get('/posts', response_model=list[models.Post])
async def read_posts():
    # TODO Ordena por fecha de publicación en orden descendente y limita a 20 resultados
    # posts = await collection_posts.find().sort("date", -1).limit(20).to_list(None)
    posts = await collection_posts.find().sort("date", -1).to_list(None)
    # Carga el usuario para cada post
    # for p in posts:
    #     p["user"] = await collection_users.find_one({"id": p["user"]})
    return posts

# Crear un nuevo post
@app.post('/posts', response_model=models.Post)
async def create_post(post: models.Post):
    # Convierte el objeto Pydantic Post en un diccionario
    post_dict = post.model_dump()
     # Inserta el nuevo post en la colección de posts en la base de datos
    result = await collection_posts.insert_one(post_dict)
    post.id = str(result.inserted_id)
    # Actualiza el campo "id" del post en la base de datos con su ID único
    result = await collection_posts.update_one({"id": ""}, {"$set": {"id": post.id}})
    # Retorna el post creado como respuesta
    return post

# Eliminar un post por su ID
@app.delete('/posts/{id}')
async def delete_post(id: str):
    # Busca el post en la base de datos por su ID
    post = await collection_posts.find_one({"id": id})
    # Si el post no se encuentra, se lanza una excepción HTTP 404
    if post is None:
        raise HTTPException(status_code=404, detail="Post no encontrado")
     # Elimina el post de la colección de posts en la base de datos
    await collection_posts.delete_one({"id": id})
    # Retorna un mensaje indicando que el post ha sido eliminado
    return {"mensaje": "Post eliminada"}








# autenticar usuario
@app.post('/authenticate', response_model=models.UserAccount)
async def authenticate(user: models.User):
    # Se obtienen los datos del usuario desde el modelo y se crea un diccionario
    user_dict = user.model_dump()
    #Se busca el usuario en la colección de usuarios por nombre y contraseña
    result = await collection_users.find_one({"name": user_dict["name"], "password": user_dict["password"]})
    # Si se encuentra el usuario, se busca su información de cuenta en la colección de cuentas de usuario
    if result is not None:
        result = await collection_user_accounts.find_one({"name": user_dict["name"]})
         # Se devuelve la información de la cuenta de usuario (o None si la autenticación falla)
    return result



# Crear una nuevo usuario
@app.post('/users', response_model=models.User)
async def create_user(user: models.User):
    user_dict = user.model_dump()
    result = await collection_users.insert_one(user_dict)
    user_dict['id'] = str(result.inserted_id)
    return user

# Eliminar una usuario por su ID
@app.delete('/users/{id}', response_model=dict)
async def delete_user(id: str):
    user = await collection_users.find_one({"name": id})
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await collection_users.delete_one({"name": id})
    await collection_user_accounts.delete_one({"name": id})
    await collection_posts.delete_many({"user": id})
    return {"mensaje": "Usuario eliminado"}



#Aniadir acountUser
@app.get('/useraccount/{nombre}', response_model=models.UserAccount)
async def get_user_account(nombre: str):
    # Buscar el usuario en la base de datos
    user = await collection_user_accounts.find_one({"name": nombre})
    
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Crear una instancia de UserAccount con los datos del usuario
    user_account = models.UserAccount(name=user["name"], profilePicture=user["profilePicture"], aboutMe=user["aboutMe"])
     # Devolver la información de la cuenta de usuario como respuesta del endpoint
    return user_account

#modificar acountUser
@app.put('/useraccount', response_model=models.UserAccount)
async def modify_user(updated_user: models.UserAccount):
    # Realizar la actualización en la base de datos
    #Se actualizan los campos del usuario con los nuevos valores utilizando el operador $set de MongoDB.
    await collection_user_accounts.update_one({"name": updated_user.name}, {"$set": {"aboutMe": updated_user.aboutMe}})
    await collection_user_accounts.update_one({"name": updated_user.name}, {"$set": {"profilePicture": updated_user.profilePicture}})

    # Devolver el usuario actualizado
    return updated_user



@app.post('/useraccount', response_model=models.UserAccount)
async def create_user_account(user: models.UserAccount):
    user_dict = user.model_dump()
    result = await collection_user_accounts.insert_one(user_dict)
    user_dict['id'] = str(result.inserted_id)
    return user


#En este paso, verificamos si el script está siendo ejecutado directamente y, en ese caso, iniciamos el servidor FastAPI en el puerto 8000.  
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)



    
