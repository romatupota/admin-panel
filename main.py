import uvicorn
import os
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Field, SQLModel, create_engine
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.middleware.sessions import SessionMiddleware

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
SECRET_KEY = "jpagjpagjpg"

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            request.session.update({"user_id": "admin_logged_in"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("user_id") == "admin_logged_in"

auth_backend = AdminAuth(secret_key=SECRET_KEY)

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(title="Назва")

SQLModel.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY,
    session_cookie="admin_session",
    same_site="lax"
)

admin = Admin(app, engine, authentication_backend=auth_backend)

class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.name]
    name = "Об'єкт"
    name_plural = "Об'єкти"

admin.add_view(ItemAdmin)

@app.get("/")
def root():
    return RedirectResponse(url="/admin")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n СЕРВЕР ЗАПУСКАЄТЬСЯ НА ПОРТУ {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)