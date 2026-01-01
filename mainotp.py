from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from twilio.rest import Client
import os

# Load Twilio credentials
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
VERIFY_SID = os.getenv("TWILIO_VERIFY_SID")

client = Client(TWILIO_SID, TWILIO_AUTH)

app = FastAPI()

# ----------------------------------------
# FRONTEND 1 — ENTER PHONE NUMBER
# ----------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home_page():
    return """
    <h2>Verify Your Phone Number</h2>
    <form action="/send-otp" method="post">
        <input name="phone" placeholder="+91XXXXXXXXXX" required>
        <button type="submit">Send OTP</button>
    </form>
    """


# ----------------------------------------
# BACKEND — SEND OTP
# ----------------------------------------
@app.post("/send-otp")
async def send_otp(request: Request):
    form = await request.form()
    phone = form.get("phone")

    client.verify.v2.services(VERIFY_SID).verifications.create(
        to=phone,
        channel="sms"
    )

    return HTMLResponse(f"""
        <h3>OTP sent to {phone}</h3>
        <form action="/verify-otp" method="post">
            <input name="phone" value="{phone}" hidden>
            <input name="code" placeholder="Enter OTP" required>
            <button type="submit">Verify</button>
        </form>
    """)


# ----------------------------------------
# BACKEND — VERIFY OTP
# ----------------------------------------
@app.post("/verify-otp")
async def verify_otp(request: Request):
    form = await request.form()
    phone = form.get("phone")
    code = form.get("code")

    result = client.verify.v2.services(VERIFY_SID).verification_checks.create(
        to=phone,
        code=code
    )

    if result.status == "approved":
        return HTMLResponse(f"""
            <h2>🎉 Number Verified!</h2>
            <p>{phone} is now a verified caller ID in Twilio.</p>
        """)
    else:
        return HTMLResponse("""
            <h2>❌ Invalid Code</h2>
            <a href="/">Try Again</a>
        """)


# ----------------------------------------
# RUN SERVER (local only)
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
