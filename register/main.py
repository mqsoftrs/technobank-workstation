import base64
import json
import logging
import sqlite3
from io import BytesIO

import qrcode
import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from qr_and_mail.main import make_qr_code_and_send_email

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

DB = sqlite3.connect(
    r"../db/participants.db",
    check_same_thread=False
)


templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def make_register_qr_code_image():
    qr_img = qrcode.make('https://technobank-register.eu.ngrok.io')
    qr_img.save("register_qr_code.png", format="PNG")


@app.get("/")
def register(req: Request):
    return templates.TemplateResponse(
        'index.html',
        context={
            'request': req,
            'message': None
        }
    )


@app.post("/")
def register(
    req: Request,
    company: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    ticket_type: str = Form(...),
    position: str = Form(...),
    mobile: str = Form(...),
    address: str = Form(...),
    city: str = Form(...)
):
    # check if email is already registered
    if len(DB.execute("select email from participants where email = ?", (email,)).fetchall()) > 0:
        return templates.TemplateResponse(
            'index.html',
            context={
                'request': req,
                'message': f"Email {email} is already registered."
            }
        )

    # store registration data into database
    DB.execute(
        "insert into participants values (?,?,?,?,?,?,?,?,?,?,0,CURRENT_TIMESTAMP)",
        (
            company,
            full_name,
            email,
            ticket_type,
            position,
            mobile,
            address,
            city,
            None,
            None
        )
    )
    DB.commit()
    logger.info(f"registration data for {email} saved to database")

    make_qr_code_and_send_email(full_name, email)
    logger.info(f"email with QR code sent to {email}")

    return templates.TemplateResponse(
        'index.html',
        context={
            'request': req,
            'message': f"Thank You! Email is sent to {email}."
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9090)
