from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
from pydantic import BaseModel, Field
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel 
from fastapi.encoders import jsonable_encoder

app = FastAPI()

app.title ="mi aplicacion sencilla"
app.version = "0.1.1"
Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
    async def __call__(self, Request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data["email"] != "admin@gamil.com":
            raise HTTPException(status_code=401, detail="invalid user")

class User (BaseModel):
    email:str
    password:str 

class Movie(BaseModel): 
    id: Optional[int] = None
    title: str = Field(default="Nombre pelicula",min_length=2, max_length=50)
    overview: str = Field(default="descripcion de la pelicula" , min_length=50)
    year: int = Field(default=2023, le=2023)
    rating: float = Field(default=10, ge=0, le=10)
    category: str = Field(default="comedia" ,min_length=4, max_length=15) 



@app.get("/", tags=["home"])
def message():
    return HTMLResponse(content="<h1> Mi aplicacion basica </h1> ")


@app.get("/movies", tags=["movies"], response_model=list[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> list[Movie]: 
    db = session()
    result = db.Query(MovieModel).all() # SELECT * FROM movies
    return JSONResponse(status_code=200, content=jsonable_encoder(result))

@app.get("/movies/{id}", tags=["movies"], status_code=200, response_model=Movie)
def get_movie(id: int) -> Movie:
    db = session()
    result = db.Query(MovieModel).filter(MovieModel.id == id).first()
    if result:
        return JSONResponse(content=result, status_code=200)    
    else:
        return JSONResponse(content={"message":"Movie not found"}, status_code=404) 
        
@app.get("/movies/" ,tags=["movies"], response_model=list[Movie])
def get_movie_by_category(category: str) -> list [Movie]:
    db = db.Query(MovieModel).filter(MovieModel.category == category).all()
    if result:
        return JSONResponse(content=jsonable_encoder(result), status_code=200)
    else:
        return JSONResponse(content={"message": "Movie not found"}, status_code=404)
    
@app.post("/movies", tags=["movies"], response_model=dict, status_code=201)
def create_movie(movie: Movie) -> dict:
    db = session()
    new_movie = MovieModel(**movie.model_dump())
    db.add(new_movie)
    db.commit() 
    return JSONResponse(content={"message": "Movie created successfully"},
                        status_code=201)  
    
@app.put("/movies/{id}", tags=["movies"], response_model=dict, status_code=200)
def update_movie(id: int, movie:Movie) -> dict: 
    db= session()
    result = db.Query(MovieModel). filter (MovieModel.id == id).first()
    if not result:
        return JSONResponse(content={"message":"Movie update successfully"}, status_code=404)
    result.title = movie.title
    result.overview = movie.overview
    result.year = movie.year
    result.rating = movie.rating
    result.category = movie.category
    db.commit()
    return JSONResponse(content={"message":"Movies not found"}, status_code=404)

@app.delete("/movies/{id}", tags=["movies"], response_model=dict)
def delete_movie(id: int) -> dict:
    db =session()
    result = db.Query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(content={"message": "Movie delated successfully"}) 
    db.delete(result)
    db.commit()
    return JSONResponse(content={"message":"Movie update successfully"}, status_code=404)

@app.post("/login", tags=["auth"], response_model=dict, status_code= 200)
def login(user:User):
    if user.email=="admin@gmail.com" and user.password == "admin":
        token = create_token(data=user.model_dump())
        return JSONResponse(content={"token":token}, status_code=200)