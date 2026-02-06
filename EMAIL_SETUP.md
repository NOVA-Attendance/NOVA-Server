# 📧 Email Setup for NOVA

## Quick Setup

### Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Step Verification** on your Gmail account
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate an App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "NOVA" as the name
   - Copy the 16-character password

3. **Create `.env` file** in `NOVA-Server` folder:
   ```env
   EMAIL_ENABLED=true
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_SENDER=your-email@gmail.com
   EMAIL_PASSWORD=your-16-char-app-password
   ```

### Option 2: Other Email Providers

**Outlook/Hotmail:**
```env
EMAIL_SMTP_SERVER=smtp-mail.outlook.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
```

**Yahoo:**
```env
EMAIL_SMTP_SERVER=smtp.mail.yahoo.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
```

**Custom SMTP:**
```env
EMAIL_SMTP_SERVER=your-smtp-server.com
EMAIL_SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_SENDER=your-email@domain.com
EMAIL_PASSWORD=your-password
```

## Testing

1. Make sure `.env` file exists with your credentials
2. Restart the backend server
3. Try registering or logging in
4. Check your email inbox for the verification code

## Troubleshooting

- **Email not sending?** Check console for error messages
- **Gmail blocking?** Make sure you're using an App Password, not your regular password
- **Still not working?** The system will fall back to showing the code in console/response

## Disable Email (Dev Mode)

Set in `.env`:
```env
EMAIL_ENABLED=false
```

This will show codes in console and API response for testing.
