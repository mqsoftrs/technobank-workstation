import base64
import json
import logging
import time
from io import BytesIO

import pandas as pd
import qrcode
from postmarker.core import PostmarkClient

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename="bulk.log", filemode="a",
                        format="%(levelname)s %(asctime)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger()

    
postmark = PostmarkClient(server_token='529ab88d-3b3c-464d-bab3-a71e9bf932ee')

TAG = "Technobank2022_0404"


def report():
    for msg in postmark.messages.outbound.all(tag=TAG):
        print(msg)


def make_qr_code_and_send_email(full_name, email):
    # generate ID
    id = base64.b64encode(email.encode()).decode()
    logger.info(f"email={email}, id={id}")
    # make QR code
    qr_img = qrcode.make(f"https://technobank.eu.ngrok.io/{id}/print")
    logger.info("QR code make completed")
    # store QR code in string
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_img_str = base64.b64encode(buffered.getvalue()).decode()
    logger.info("QR code save to img file completed")
    try:
        logger.info('-----------------------------------------------------')
        res = postmark.emails.send(
            From='Technobank Registration<office@technobank.rs>',
            # To=f"nik.mirkovic.84+__{email.replace('@','__')}@gmail.com",
            To=f"jovan+__{email.replace('@','__')}@mqsoft.rs",
            Tag=TAG,
            Subject='Technobank 2022 Registration QR Code',
            HtmlBody=f'<h3>Hello {full_name}</h3> <p>Thank You for registering for Technobank 2022.</p> <p>Your registration QR code is attached.<br>Please show it on registration desk.</p> <p>See You on April 6th and 7th in Crowne Plaza Hotel Belgrade.</p> <p>Very best regards,<br> Technobank Organizing Committee<br> +381117443140</p>',
            Attachments=[
                {
                    "Name": "qr.png",
                    "Content": qr_img_str,
                    "ContentType": "image/PNG"
                }
            ]
        )
        if res['ErrorCode'] == 0:
            logger.info(
                f"email sent {email} {index}/{len(df.index)} with MessageID={res['MessageID']}")
        else:
            logger.error("Not sent..")
    except:
        logger.error("Exception occurred..")


def bulk():
    logger.info("Bulk emails with QR code sending started..")
    df = pd.read_excel(r'participants.xlsx')
    data_sql = open("data.sql", "a")
    for index, row in df.iterrows():
        print(f"processing index= {index}..")
        if index > 9:
            break
        time.sleep(1)
        # extract email and full name
        email = row["e-mail"]
        full_name = f"{row['Ime']} {row['Prezime']}"
        full_name_ = f"{row['Ime']}_{row['Prezime']}"
        if pd.isnull(email):
            logging.error(f"skipping row: {full_name}")
            continue
        # make_qr_code_and_send_email(full_name, email)
        # extract othre data
        company = row['FIRMA']
        ticket_type = row['ticket_type']
        position = row['funkcija']
        mobile = ""
        address = row['Adresa']
        city = f"{row['Post.br.']} {row['Mesto']} {row['Drzava']}"
        data_sql.write(f"INSERT OR REPLACE INTO participants VALUES('{company}','{full_name}', '{email}', '{ticket_type}', '{position}', '{mobile}', '{address}', '{city}', NULL, NULL, 0, CURRENT_TIMESTAMP);\n")
    logger.info('-----------------------------------------------------')
    logger.info("Bulk emails with QR code sending completed.")
    data_sql.close()


if __name__ == "__main__":
    print("Bulk emails with QR code sending started..")
    bulk()
    print("Bulk emails with QR code sending completed.")
