# Notification Setup Guide

Get instant alerts via WhatsApp, SMS, or Email when users ask questions!

---

## 🎯 Available Notification Channels

1. **📧 Email** (via SendGrid) - Recommended
2. **📱 SMS** (via Twilio)
3. **💬 WhatsApp** (via Twilio)
4. **💼 Slack** (via Webhook)
5. **🎮 Discord** (via Webhook)

---

## 🚀 Quick Setup (Choose Your Preferred Method)

### Option 1: Email Notifications (Easiest) ⭐

**Step 1: Get SendGrid API Key**
1. Go to https://sendgrid.com
2. Sign up for free account (100 emails/day free)
3. Go to Settings → API Keys
4. Create new API key with "Mail Send" permissions
5. Copy the API key

**Step 2: Configure**
```bash
# Edit .env file
NOTIFICATIONS_ENABLED=true
NOTIFICATION_CHANNELS=email
SENDGRID_API_KEY=SG.your-api-key-here
NOTIFICATION_EMAIL_FROM=noreply@yourdomain.com
NOTIFICATION_EMAIL_TO=your-email@gmail.com
```

**Done!** You'll now get emails when users ask questions.

---

### Option 2: WhatsApp Notifications (Most Popular) 💬

**Step 1: Get Twilio Account**
1. Go to https://www.twilio.com
2. Sign up for free trial ($15 credit)
3. Get your Account SID and Auth Token from dashboard
4. Enable WhatsApp sandbox: https://www.twilio.com/console/sms/whatsapp/sandbox

**Step 2: Join WhatsApp Sandbox**
1. Send WhatsApp message to Twilio number
2. Send the code they provide (e.g., "join abc-def")
3. You're now connected!

**Step 3: Configure**
```bash
# Edit .env file
NOTIFICATIONS_ENABLED=true
NOTIFICATION_CHANNELS=whatsapp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
WHATSAPP_FROM_NUMBER=whatsapp:+14155238886
WHATSAPP_TO_NUMBER=whatsapp:+15551234567  # Your WhatsApp number
```

**Done!** You'll get WhatsApp messages instantly.

---

### Option 3: SMS Notifications 📱

**Step 1: Get Twilio Phone Number**
1. Sign up at https://www.twilio.com
2. Get a phone number (free with trial)
3. Copy Account SID and Auth Token

**Step 2: Configure**
```bash
# Edit .env file
NOTIFICATIONS_ENABLED=true
NOTIFICATION_CHANNELS=sms
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890  # Your Twilio number
TWILIO_TO_NUMBER=+1234567890    # Your mobile number
```

---

### Option 4: Slack Notifications 💼

**Step 1: Create Slack Webhook**
1. Go to https://api.slack.com/messaging/webhooks
2. Create new app
3. Enable Incoming Webhooks
4. Add webhook to workspace
5. Copy webhook URL

**Step 2: Configure**
```bash
# Edit .env file
NOTIFICATIONS_ENABLED=true
NOTIFICATION_CHANNELS=slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

### Option 5: Discord Notifications 🎮

**Step 1: Create Discord Webhook**
1. Go to your Discord server
2. Server Settings → Integrations → Webhooks
3. Create webhook
4. Copy webhook URL

**Step 2: Configure**
```bash
# Edit .env file
NOTIFICATIONS_ENABLED=true
NOTIFICATION_CHANNELS=discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK/URL
```

---

## 🎨 Multiple Channels

You can enable multiple channels at once:

```bash
NOTIFICATIONS_ENABLED=true
NOTIFICATION_CHANNELS=email,whatsapp,slack

# Configure all channels you want to use
SENDGRID_API_KEY=...
TWILIO_ACCOUNT_SID=...
SLACK_WEBHOOK_URL=...
```

---

## 📋 What You'll Receive

### Email Example:
```
Subject: 🔔 New Bhagavad Gita Question

⏰ Time: 2026-02-21 01:30:45
❓ Question: What is karma yoga?
🌐 IP: 192.168.1.1
📍 Location: San Francisco, CA

🔗 View in dashboard: https://your-dashboard-url.com
```

### WhatsApp/SMS Example:
```
🔔 New Question Alert

⏰ Time: 2026-02-21 01:30:45
❓ Question: What is karma yoga?

🔗 View dashboard
```

---

## 🧪 Testing Your Setup

After configuration, test it:

```bash
# Start your API
python main_v2.py

# In another terminal, send a test question
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Test notification - What is dharma?"}'
```

You should receive a notification within seconds!

---

## 💰 Cost Breakdown

### Free Tiers:
- **SendGrid**: 100 emails/day free
- **Twilio Trial**: $15 credit (≈500 SMS or WhatsApp messages)
- **Slack**: Free
- **Discord**: Free

### Paid Plans (if you exceed free tier):
- **SendGrid**: $19.95/month for 50k emails
- **Twilio SMS**: $0.0075 per message
- **Twilio WhatsApp**: $0.005 per message

**Recommendation**: Start with email (free) and add WhatsApp if needed.

---

## 🎯 Advanced Features

### Daily Summary Email

Add to your cron or scheduler:

```python
# Send daily summary at 9 PM
from src.services.notification_service import NotificationService

notifier = NotificationService()
notifier.send_daily_summary({
    "total_questions": 150,
    "unique_users": 45,
    "avg_response_time": 1234.56,
    "top_question": "What is karma yoga?"
})
```

### Custom User Info

Add user details to notifications:

```python
# In routes.py
notification_service.send_question_alert(
    question=request.question,
    user_info={
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "location": "San Francisco, CA"  # Use IP geolocation service
    }
)
```

---

## 🔧 Troubleshooting

### Not receiving notifications?

1. **Check logs**:
```bash
tail -f logs/app.log | grep notification
```

2. **Verify settings**:
```bash
# Check if enabled
grep NOTIFICATIONS_ENABLED .env

# Test API keys
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer YOUR_API_KEY"
```

3. **Test individual channels**:
```python
from src.services.notification_service import NotificationService

notifier = NotificationService()
result = notifier._send_email("Test message")
print(result)
```

### WhatsApp not working?

- Make sure you joined the sandbox
- Check number format: `whatsapp:+15551234567`
- Verify Twilio credentials

### Email going to spam?

- Verify sender domain in SendGrid
- Add SPF/DKIM records
- Use a custom domain

---

## 📊 Monitoring

Track notification delivery:

```bash
# View notification logs
grep "notification sent" logs/app.log

# Count notifications today
grep "$(date +%Y-%m-%d)" logs/app.log | grep "notification" | wc -l
```

---

## 🔐 Security Best Practices

1. **Never commit API keys**:
```bash
# .env is in .gitignore
echo ".env" >> .gitignore
```

2. **Use environment variables**:
```bash
# Set in Cloud Run
gcloud run services update bhagavad-gita-api \
  --set-env-vars SENDGRID_API_KEY=your-key
```

3. **Rotate keys regularly**:
- Change API keys every 90 days
- Use different keys for dev/prod

---

## 🎉 You're All Set!

Once configured, you'll automatically receive notifications whenever someone asks a question through your Bhagavad Gita API!

**Questions?** Check the logs or test with the curl command above.
