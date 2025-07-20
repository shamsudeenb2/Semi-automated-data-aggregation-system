import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect,Depends, File, UploadFile, HTTPException,Form
from fastapi.middleware.cors import CORSMiddleware
from app.utils.db import engine
from app.models.stateModel import Base
# from fastapi import WebSocket, WebSocketDisconnect
from app.notifications import manager
import asyncio
from app.utils.db import SessionLocal
from app.email_handler import process_emails
from sqlalchemy import select

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.db import get_db
from app.models.stateModel import User
from app.data_processing import process_excel_file
from passlib.context import CryptContext
from jose import JWTError,jwt
import datetime
from typing import Annotated
from app.socket_server import socket_app, sio
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware
from socketio import AsyncServer
from socketio.asgi import ASGIApp

from app.utils.schemas import UserCreate

from app.routes.download_csv_file import router as download_router
from app.routes import state_routes
from app.routes import count_file_routes
from app.routes import count_mail_volume
from app.routes.charts_routes import get_total_month
from app.routes.charts_routes import submission_tracker_routes
from app.routes.charts_routes import missed_months_routes
from app.routes.charts_routes import mail_type_foreign_domestic
from app.routes.charts_routes import get_trend_by_sheet_and_month
from app.routes.charts_routes import get_total_postoffice
from app.routes.charts_routes import get_total_state





@asynccontextmanager
async def lifespan(app: FastAPI):
     async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
     yield

app = FastAPI(lifespan=lifespan)


# bearer_scheme = HTTPBearer()
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# Allow requests from your Next.js frontend
origins = [
    "http://localhost:3000",  # or your deployed frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # allow specific origins
    allow_credentials=True,
    allow_methods=["*"],             # allow all HTTP methods
    allow_headers=["*"],             # allow all headers
)

SECRET_KEY = "secret"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["md5_crypt"])

def hash_password(password: str):
    print("hashing password")
    return pwd_context.hash(password)

def verify_password(plain, hashed): # type: ignore
    return pwd_context.verify(plain, hashed) # type: ignore

def create_access_token(data: dict): # type: ignore
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM) # type: ignore

def decode_token(token: str): 
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# Mount the socket app
app.mount("/ws", socket_app)

sio = AsyncServer(async_mode="asgi", cors_allowed_origins="*")
sio_app = ASGIApp(sio)
#  import socketio
#     import uvicorn

#     sio = socketio.AsyncServer()
#     app = socketio.ASGIApp(sio, static_files={
#         '/': 'index.html',
#         '/static': './public',
#     })
#     uvicorn.run(app, host='127.0.0.1', port=5000)

# Wrap both into ASGI application
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("notification", "You are connected 🎉", to=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@app.get("/")
def read_root():
    return {"Hellow":"world"}

@app.get("/checkemail")
def checkmail():
    # return {"message": "AutoCollate System Backend is Running"}
    async def _check():
        async with SessionLocal() as db:
            await process_emails(db)

    try:
        asyncio.run(_check())
        print("Email processing task completed successfully.")
    except Exception as e:
        print(f"Error in check_email task: {e}")
    return{"msg":"Email checking completed"}



@app.post("/register")
async def register(user: UserCreate,
    db: AsyncSession = Depends(get_db)):
    hashed_password=hash_password(user.password)
    user = User(username=user.username, hashed_password=hashed_password ,name=user.name,phone_number=user.phone_number,email=user.email,role=user.role)
    db.add(user)
    await db.commit()
    return {"message": "User created"}

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(get_db)):
    statement = select(User).where(User.username == form_data.username)
    result = await db.execute(statement) 
    user = result.scalar_one_or_none() 
    if not user or not verify_password(form_data.password, user.hashed_password): # type: ignore
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": create_access_token({"sub": "1234567890","name": user.username,"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}),"name":user.name,"role":user.role, "token_type": "bearer"} # type: ignore

@app.get("/user")
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)): 
    try:
        # credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
        # tokens = credentials.credentials
        payload = decode_token(token)
        username = payload.get("name")
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/upload-xlsx")
async def upload_xlsx(state:str= Form(...), month:str= Form(...), file: UploadFile = File(...), db: AsyncSession = Depends(get_db)): 
    print(f"state: {state}, month: {month}, file: {file.filename}")
    result =  await process_excel_file(file, "uploaded",state, month,db)
    # await sio.emit("upload_notification", {
    # "message": f"📬 {state} uploaded a file for {month}!"
    #  })
    return {"message": "File uploaded and processed", "result": result}

app.include_router(download_router, prefix="/api") #routes to download
app.include_router(state_routes.router) #routes to get distinc state
app.include_router(count_file_routes.router) #route to count the total number of file submitted this year, this month, via upload and via download

app.include_router(get_total_month.router) # summary for months to show what is generated for each month in a barchart 
app.include_router(submission_tracker_routes.router) # Get the state that submit this month, and missed this month
app.include_router(missed_months_routes.router) # Get the state that missed privious months
app.include_router(mail_type_foreign_domestic.router) # Get the total of foreign and domestic for a month for pie chart
app.include_router(get_trend_by_sheet_and_month.router) # Get the total of mail deliver throught particular channels and months
app.include_router(get_total_postoffice.router)# Get the Total generated by postoffice using state and postoffice
app.include_router(get_total_state.router)# Get the Total generated by state for a month 
app.include_router(count_mail_volume.router) #route to count the total number of mail submitted this year, this month, via upload and via download


# @app.websocket("/ws/notifications")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
# Emit message from backend
# @app.post("/notify-upload-success")
# async def notify_upload_success():
#     await sio.emit("upload_notification", {"message": "New file uploaded successfully!"})
#     return {"status": "notified"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


# sudo service redis-server restart  "this the code to start redis in wsl ubuntu"

#.venv/Scripts/activate
# celery -A app.celery_worker beat --loglevel=info "this is the code start beat scheduler in any terminal eg vs cod terminal
# celery -A app.celery_worker worker --loglevel=info -P solo  "this is the code to start celery worker"
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000  "this is the code to start the main app or unicorn server
