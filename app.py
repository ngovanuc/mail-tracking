import os
import sys
import warnings
import uuid
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
from argon2 import PasswordHasher

from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware

import fastapi
from fastapi import FastAPI, Depends, Form, HTTPException, status, Request, Cookie, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.authentication.init import mail_tracking_database
from src.authentication.init import users_collection

from src.conferences.init import conferences_collection
from src.conferences.create_new_conference import create_new_conference
from src.conferences.get_conference_information import get_conference_information
from src.conferences.get_conference_information import ratio_report
from src.conferences.get_conference_information import mail_sent_this_week

from src.processing_upload.processing_contacts import process_uploaded_excel

from src.email_sending.get_list_sending import contacts_to_send
from src.email_sending.send_email import send

os.system("cls")

app = FastAPI()
templates = Jinja2Templates(directory=["templates", "uploaded"])
app.mount("/public", StaticFiles(directory="public"), name="public")
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/uploaded", StaticFiles(directory="uploaded"), name="uploaded")

# Initializing system
# Connect to DB...

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Main endpoint that renders a welcome HTML template.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Welcome to the Mail Tracking API",
            "login_url": "/login"
        }
    )


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    ph = PasswordHasher()
    user = users_collection.find_one({"gmail_account": username})
    if user:
        try:
            if ph.verify(user['gmail_password'], password):
                return RedirectResponse("/home", status_code=status.HTTP_302_FOUND)
        except Exception:
            pass

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Mail Tracking API",
            "message": "Sai thông tin đăng nhập!",
            "login_url": "/login",
            "login_error": True
        }
    )


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    conferences = mail_tracking_database["conferences_collection"].find().to_list()
    if len(conferences) == 0:
        no_conference = "No conferences available ❌"
    else:
        no_conference = ""
    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request,
            "no_conference": no_conference,
            "title": "Mail Tracking Home",
            "conferences": conferences
        }
    )


@app.post("/home/addconference")
async def add_conference(
    request: Request,
    name: str = Form(...),
    location: str = Form(...),
    date: str = Form(...),
    link_conference: str = Form(...),
    description: str = Form(""),
    excel_file: UploadFile | None = File(None),
    subject: str = Form(None),
    html_template: UploadFile | None = File(None),
    poster: UploadFile | None = File(None)
):
    
    # Create uploaded folder
    os.makedirs("uploaded", exist_ok=True)

    # Save excel file to server
    print(excel_file)
    processed_contacts = []
    try:
        if excel_file is None or excel_file.filename == "":
            excel_filepath = None
            print("No excel file uploaded.")
        else:
            os.makedirs(f"uploaded/{name}", exist_ok=True)
            excel_filepath = f"uploaded/{name}/{excel_file.filename}"
            with open(excel_filepath, "wb") as f:
                f.write(await excel_file.read())
                print(f"Excel file saved at: {excel_filepath}")
            # Read excel file and save contacts to database
            try:
                processed_contacts = process_uploaded_excel(excel_filepath, name)
                print(f"Processed {len(processed_contacts)} contacts from excel file.")
            except Exception as e:
                print(f"Error processing excel file: {e}")
                processed_contacts = []
    except Exception as e:
        print(f"Error saving excel file: {e}")
        excel_filepath = None

    # Save HTML template file to server
    print(html_template)
    try:
        if html_template is None or html_template.filename == "":
            html_template_filepath = None
            print("No HTML template uploaded.")
        else:
            os.makedirs(f"uploaded/{name}", exist_ok=True)
            html_template_filepath = f"uploaded/{name}/{html_template.filename}"
            with open(html_template_filepath, "wb") as f:
                f.write(await html_template.read())
                print(f"HTML template saved at: {html_template_filepath}")
    except Exception as e:
        print(f"Error saving HTML template: {e}")
        html_template_filepath = None

    # Save poster to server
    print(poster)
    try:
        if poster is None or poster.filename == "":
            poster_filepath = None
            print("No poster uploaded.")
        else:
            os.makedirs(f"uploaded/{name}", exist_ok=True)
            poster_filepath = f"uploaded/{name}/{poster.filename}"
            with open(poster_filepath, "wb") as f:
                f.write(await poster.read())
                print(f"Poster saved at: {poster_filepath}")
    except Exception as e:
        print(f"Error saving poster: {e}")
        poster_filepath = None

    # Full data object
    data = {
        "name": name,
        "location": location,
        "date": date,
        "link_conference": link_conference,
        "link_id": str(uuid.uuid4()),
        "description": description,
        "excel_filepath": excel_filepath,
        "subject": subject,
        "name_template": html_template.filename if html_template else None,
        "html_template_filepath": html_template_filepath,
        "poster_filename": poster.filename if poster else None,
        "poster_filepath": poster_filepath,
        "recipients": processed_contacts,
        "total_sent": 0,
        "total_opened": 0,
        "total_clicked": 0,
        "total_failed": 0,
        "total_unsubscribed": 0,
        "total_responded": 0,
        "last_sent_time": None,
        "last_sent_count": 0,
    }

    # Lưu thông tin hội nghị vào database
    mail_tracking_database["conferences_collection"].insert_one(data)

    return RedirectResponse("/home", status_code=status.HTTP_302_FOUND)


@app.get("/home/addconference")
async def add_conference(request: Request):
    return templates.TemplateResponse("add_conference.html", {
        "request": request,
    })


@app.get("/home/{conference_name}", response_class=HTMLResponse)
async def conference_detail(request: Request, conference_name: str):
    conference = mail_tracking_database["conferences_collection"].find_one({"name": conference_name})
    if not conference:
        return HTMLResponse(f"<h2>Không tìm thấy hội nghị: {conference_name}</h2>", status_code=404)
    
    conference_analysis = await get_conference_information(conference=conference)
    ratio_analysis = await ratio_report(conference_analysis)
    sent_this_week = await mail_sent_this_week(conference_name=conference_name)
    
    return templates.TemplateResponse(
        "conference_detail.html", 
        {
            "request": request,
            "conference": conference,
            "total_recipients": conference_analysis["total_recipients"],
            "total_sent": conference_analysis["total_sent"],  
            "total_opened": conference_analysis["total_opened"],
            "total_clicked": conference_analysis["total_clicked"],
            "total_failed": conference_analysis["total_failed"],
            "total_unsubscribed": conference_analysis["total_unsubscribed"],
            "mail_sent_per_day": await mail_sent_this_week(conference_name),
            "ratio_analysis": ratio_analysis
        }
    )


@app.get("/home/{conference_name}/contacts", response_class=HTMLResponse)
async def contacts(request: Request, conference_name: str):
    conference = mail_tracking_database["conferences_collection"].find_one({"name": conference_name})
    print(f"[LOG] Loading contacts for conference: {conference_name}")
    return templates.TemplateResponse(
        "contacts.html", 
        {
            "request": request,
            "conference_name": conference_name,
            "conference": conference,
        }
    )


@app.get("/template/{conference_name}", response_class=HTMLResponse)
async def show_template(request: Request, conference_name):
    conference = mail_tracking_database["conferences_collection"].find_one({"name": conference_name})
    name_template = conference.get("name_template") if conference else None
    poster_filename = conference.get("poster_filename") if conference else None
    poster_url = request.url_for(
        "uploaded", 
        path=f"{conference_name}/{poster_filename}"
    )
    return templates.TemplateResponse(
        f"{conference_name}/{name_template}",
        {
            "request": request,
            "conference_name": conference_name,
            "html_template_filepath": name_template,
            "poster_url": poster_url
        }
    )

# Endpoint to tracking email opened
@app.get("/track/open/{conference_name}/{poster_filename}")
async def track_open(request: Request, conference_name: str, poster_filename: str):
    """Mỗi lần client mở email, server sẽ log vào tracking_collection.
    
    Đây mới chỉ log được request, còn việc biết ai mở thì chưa thể biết được.
    """
    # 1. Ghi log vào database
    mail_tracking_database["tracking_collection"].insert_one({
        "conference_name": conference_name,
        "poster_filename": poster_filename,
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "opened_at": datetime.datetime.utcnow(),
    })

    # 2. Trả lại hình ảnh poster thật (cũng có thể thay thế bằng một pixel 1x1)
    poster_path = f"uploaded/{conference_name}/{poster_filename}"
    return FileResponse(poster_path, media_type="image/png")


# Endpoint to tracking email opened
@app.get("/track/open/{tracking_id}.png")
async def track_open_pixel(request: Request, tracking_id: str):
    # Tìm email tương ứng với tracking_id
    record = mail_tracking_database["recipients"].find_one({"tracking_id": tracking_id})

    if record:
        # Ghi log mở thư
        mail_tracking_database["opens_collection"].insert_one({
            "tracking_id": tracking_id,
            "email": record["email"],
            "conference_name": record.get("conference_name"),
            "opened_at": datetime.datetime.utcnow(),
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
        })

        # Cập nhật trạng thái đã mở thư
        mail_tracking_database["recipients"].update_one(
            {"tracking_id": tracking_id},
            {"$set": {"status.opened": True, "status.date_opened": datetime.datetime.utcnow()}}
        )

    # Trả về ảnh pixel 1x1 trong suốt
    pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00' \
            b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00' \
            b'\x01\x00\x01\x00\x00\x02\x02L\x01\x00;'
    return Response(content=pixel, media_type="image/gif")

@app.get("/track/click/{tracking_id}/{link_id}")
async def track_click(request: Request, tracking_id, link_id):
    # Tìm thông tin người nhận
    recipient = mail_tracking_database["conferences_collection"].find_one({"tracking_id": tracking_id})

    # Tìm link gốc từ link_id
    link = mail_tracking_database["conferences_collection"].find_one({"link_id": link_id})

    if recipient and link:
        # Ghi log click vào database
        mail_tracking_database["clicks_collection"].insert_one({
            "tracking_id": tracking_id,
            "link_id": link_id,
            "email": recipient["email"],
            "conference_name": recipient.get("conference_name"),
            "clicked_at": datetime.datetime.utcnow(),
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
        })

        mail_tracking_database["conferences_collection"].update_one(
            {"tracking_id": tracking_id},
            {"$set": {"status.clicked": True, "status.date_clicked": datetime.datetime.utcnow()}}
        )

        # Chuyển hướng đến link gốc
        return RedirectResponse(url=link)

    return {"error": "Link not found"}, 404


# Endpoint to unsubscribe email
# @app.get("/unsubscribe/{tracking_id}", response_class=HTMLResponse)
# async def unsubscribe(request: Request, tracking_id: str):
#     # Tìm email tương ứng với tracking_id
#     record = mail_tracking_database["recipients"].find_one({"tracking_id": tracking_id})

#     if record:
#         # Cập nhật trạng thái đã hủy đăng ký
#         mail_tracking_database["recipients"].update_one(
#             {"tracking_id": tracking_id},
#             {"$set": {"status.unsubscribed": True}}
#         )
#         message = "You have successfully unsubscribed from our mailing list."
#     else:
#         message = "Invalid unsubscribe link."

#     return templates.TemplateResponse("unsubscribe.html", {
#         "request": request,
#         "message": message
#     })


# Unsubscribe by email
@app.get("/unsubscribe")
async def unsubscribe_get(request: Request):
    return templates.TemplateResponse(
        "unsubscribe.html", 
        {
            "request": request
        }
    )
@app.post("/unsubscribe")
async def unsubscribe_post(request: Request, email: str = Form(...)):
    # Tìm email trong database
    record = mail_tracking_database["recipients"].find_one({"email": email})

    if record:
        # Cập nhật trạng thái đã hủy đăng ký
        mail_tracking_database["recipients"].update_one(
            {"email": email},
            {"$set": {"status.unsubscribed": True}}
        )
        print("status 1")
        message = "You have successfully unsubscribed from our mailing list."
    else:
        print("status 2")
        message = "Email not found in our records."

    return templates.TemplateResponse(
        "unsubscribe.html", 
        {
            "request": request,
            "message": message
        }, 
    )

@app.get("/home/{conference_name}/sending")
async def sending(request: Request, conference_name: str):
    conference = mail_tracking_database["conferences_collection"].find_one({"name": conference_name})
    if not conference:
        return HTMLResponse(f"<h2>Không tìm thấy hội nghị: {conference_name}</h2>", status_code=404)
    # Check if need to send email

    contacts, message = contacts_to_send(conference)
    return templates.TemplateResponse(
        "sending.html", 
        {
            "request": request,
            "conference_name": conference_name,
            "conference": conference,
            "contacts": contacts,
            "message": message
        }
    )


@app.post("/home/{conference_name}/sending")
async def sending_action(
    request: Request, 
    conference_name: str,
    gmail: str = Form(...),
    app_password: str = Form(...),
):
    print(f"gmail: {gmail}, app_password: {app_password}")

    # Lấy danh sách gửi thư và thông tin hội nghị
    conference = mail_tracking_database["conferences_collection"].find_one({"name": conference_name})
    if not conference:
        return JSONResponse(content={"error": "Conference not found."}, status_code=404)

    contacts = contacts_to_send(conference)

    # Sử dụng StreamingResponse để gửi trạng thái theo thời gian thực
    return StreamingResponse(
        send(conference, contacts, gmail, app_password), 
        media_type="text/event-stream"
    )