import base64
import json
import logging
import shutil
import sqlite3
from os import system

import qrcode
import uvicorn
import zpl
from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

logging.basicConfig(level=logging.DEBUG)

DB = sqlite3.connect(
    r"db/participants.db",
    check_same_thread=False
)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(CORSMiddleware, allow_origins="*")


def make_find_participants_qr_code_image():
    qr_img = qrcode.make('https://technobank.eu.ngrok.io')
    qr_img.save("find_participants_qr_code.png", format="PNG")


@app.get("/")
def participants(request: Request):
    return templates.TemplateResponse(
        'index.html',
        context={
            'request': request,
            'clients': None
        }
    )


@app.post("/")
def participants(request: Request, company: str = Form(...)):
    # return all participants that match find criteria and display
    participants = [
        {
            "id": row[0],
            "company": row[1],
            "full_name": row[2],
            "email": row[3],
            "ticket_type": row[4],
            "position": row[5],
            "mobile": row[6],
            "address": row[7],
            "city": row[8],
            "code": base64.b64encode(row[3].encode()).decode(),
        }
        for row in DB.execute("select rowid, company, full_name, email, ticket_type, position, mobile, address, city from participants where company like ?", (f"%{company}%",))
    ]
    return templates.TemplateResponse(
        'index.html',
        context={
            'request': request,
            'clients': participants,
            'company_to_find': company
        }
    )


def shortit(txt: str):
    t = txt.strip()
    if len(t) < 27:
        return t
    return t[0:25]


def decode_email_and_get_data(id: str):
    # decode email
    email = base64.b64decode(id).decode()
    # find participant in the database
    rows = [
        {
            "company": row[0],
            "full_name": row[1],
            "position": row[2],
            "ticket_type": row[3]
        }
        for row in DB.execute(
            "select company, full_name, position, ticket_type from participants where email=?",
            (email,)
        )
    ]
    data = rows[0]
    return email, data


@app.post("/{id}/edit")
def edit_participant_data(
    id: str,
    req: Request,
    full_name: str = Form(...),
    ticket_type: str = Form(...),
    position: str = Form(...)
):
    email, data = decode_email_and_get_data(id)
    DB.execute(
        "update participants set full_name=?, ticket_type=?, position=? where email=?",
        (
            full_name,
            ticket_type,
            position,
            email
        )
    )
    DB.commit()
    return "Data saved. Just go back to return to the previouse screen.."

@app.get("/{id}/print")
def print_label(id: str):
    '''Print badge.'''

    email, data = decode_email_and_get_data(id)

    # save time of printing and upadte number of times printed
    DB.execute(
        "update clients set first_printed = IFNULL(first_printed, CURRENT_TIMESTAMP), last_printed = CURRENT_TIMESTAMP, num_of_times_printed = num_of_times_printed + 1 where email=? ",
        (email,)
    )
    DB.commit()

    l = zpl.Label(width=100, height=152)
    l.change_international_font()
    l.set_default_font(height=8, width=3, font='V')

    l.origin(0, 49)
    l.write_text(shortit(data["company"]),
                 line_width=65, justification='C')
    l.endorigin()

    l.origin(0, 56)
    l.write_text(shortit(data["full_name"]), line_width=65, justification='C')
    l.endorigin()

    l.origin(0, 63)
    l.write_text(shortit(data["position"]),
                 line_width=65, justification='C')
    l.endorigin()

    l.origin(0, 70)
    l.write_text(shortit(data["ticket_type"]),
                 line_width=65, justification='C')
    l.endorigin()

    file_name = email.replace("@", "__")
    with open(f"./labels/{file_name}.epl", "wb") as output:
        shutil.copyfileobj(l.preview(), output)

    # system("copy /B label.epl \\DESKTOP-3SSRE15\GK420t")

    return "Your badge should be sent to printer:)"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
