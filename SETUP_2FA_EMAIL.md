# 🔐 Setup 2-Step Verification Email (Like Gmail, Facebook, etc.)

## Quick Setup (5 minutes)

### Step 1: Install Python Package
```bash
cd /Users/Eknoor/NOVA-UI/NOVA-Server
pip3 install python-dotenv
```

### Step 2: Run Setup Script
```bash
python3 setup_email.py
```

Follow the prompts to enter your email credentials.

### Step 3: Test Email
```bash
python3 test_email.py
```

This will send a test email to verify everything works.

### Step 4: Restart Backend
```bash
python3 app.py
```

**Done!** Now 2-step verification will work like professional websites - codes sent via email!

---

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create `.env` file in `NOVA-Server` folder:

```env
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### 2. Get Gmail App Password:

1. Go to: https://myaccount.google.com/apppasswords
2. Enable 2-Step Verification if not already enabled
3. Select "Mail" and "Other (Custom name)"
4. Enter "NOVA" as the name
5. Click "Generate"
6. Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)
7. Paste it in `.env` file as `EMAIL_PASSWORD` (remove spaces)

### 3. Restart Backend:
```bash
python3 app.py
```

---

## How It Works Now

✅ **When email is configured:**
- Codes are sent to user's email automatically
- Codes are NOT shown in browser/console (secure)
- Works exactly like Gmail, Facebook, etc.
- Professional 2-step verification

⚠️ **When email is NOT configured:**
- Codes shown in console/alert (dev mode only)
- Warning message appears
- Not secure - for testing only

---

## Troubleshooting

**Email not sending?**
1. Run `python3 test_email.py` to diagnose
2. Check console for error messages
3. Verify App Password is correct (not regular password)
4. Check spam folder

**Still not working?**
- Make sure `.env` file is in `NOVA-Server` folder
- Restart backend after creating `.env`
- Check that `EMAIL_ENABLED=true`

---

## Security Notes

- ✅ Codes are NEVER included in API response when email works
- ✅ Codes expire in 10 minutes
- ✅ Each code can only be used once
- ✅ Professional-grade 2FA implementation

---

**Once configured, your 2-step verification will work exactly like major websites!** 🎉
