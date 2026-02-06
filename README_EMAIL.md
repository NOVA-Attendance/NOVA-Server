# 📧 Email Setup Guide

## Quick Start

The system works in **two modes**:

### 1. **Dev Mode (Default)** - No Setup Required
- Codes are shown in console and API response
- Perfect for development and testing
- No email configuration needed

### 2. **Email Mode** - Optional Setup
- Codes are sent via email
- Requires email configuration
- Better for production/demo

---

## Enable Email (Optional)

### Step 1: Install Dependency
```bash
pip3 install python-dotenv
```

### Step 2: Create `.env` File
Create a file named `.env` in the `NOVA-Server` folder:

```env
EMAIL_ENABLED=true
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### Step 3: Get Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Enable 2-Step Verification if not already enabled
3. Generate an "App Password" (16 characters)
4. Copy it to `.env` file as `EMAIL_PASSWORD`

### Step 4: Restart Server
The server will automatically load the `.env` file.

---

## Current Status

**Email is currently DISABLED by default** (dev mode).

To enable:
1. Set `EMAIL_ENABLED=true` in `.env` file
2. Add your email credentials
3. Restart the server

---

## Troubleshooting

- **Email not sending?** Check console for error messages
- **Gmail blocking?** Make sure you're using an App Password, not your regular password
- **Still not working?** The system will automatically fall back to showing codes in console

---

## Other Email Providers

**Outlook:**
```env
EMAIL_SMTP_SERVER=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587
```

**Yahoo:**
```env
EMAIL_SMTP_SERVER=smtp.mail.yahoo.com
EMAIL_SMTP_PORT=587
```
