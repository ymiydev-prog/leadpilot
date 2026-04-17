# LeadPilot

B2B lead generation SaaS for the Spanish market.

## 🌐 Live URLs

- **Frontend**: https://leadpilot.es
- **API**: https://nv96hw8d.functions.insforge.app
- **Dashboard**: https://leadpilot.es/dashboard

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│  Cloudflare/    │────▶│  Insforge Edge       │────▶│  Insforge    │
│  Vercel         │     │  Functions (API)     │     │  Database    │
│  (Frontend)     │     │                     │     │              │
└─────────────────┘     └──────────────────────┘     └─────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Firecrawl   │
                        │  (Lead Gen)  │
                        └──────────────┘
```

## 🛠️ Stack

- **Frontend**: HTML/CSS/JS (static, hosted on InsForge/Vercel)
- **Backend**: InsForge Edge Functions (TypeScript/Deno)
- **Database**: InsForge PostgreSQL
- **Lead Search**: Firecrawl API
- **Email**: Resend
- **Telegram**: OpenClaw Bot

## 📁 Project Structure

```
leadpilot/
├── index.html              # Landing page
├── dashboard/              # Dashboard app (HTML/JS)
├── chat/                   # Chat page
├── contact/                # Contact page
├── privacy/                # Privacy policy
├── terms/                  # Terms of service
├── insforge/
│   └── functions/
│       └── api/
│           └── index.ts    # API Edge Function
├── backend/
│   └── chat_bridge.py      # OpenClaw Telegram bridge
├── .env                    # Environment variables (gitignored)
├── _redirects              # Cloudflare/InsForge redirects
└── README.md
```

## ⚙️ Setup

### 1. Environment Variables

Create `.env` with:
```bash
INSFORGE_URL=https://nv96hw8d.eu-central.insforge.app
INSFORGE_API_KEY=your_key
JWT_SECRET=your_secret
FIRECRAWL_API_KEY=your_key
RESEND_API_KEY=your_key
```

### 2. Deploy API

```bash
npx @insforge/cli functions deploy api
```

### 3. Deploy Frontend

```bash
npx @insforge/cli deployments deploy .
```

## 🔌 API Endpoints

### Auth
- `POST /api/register` - Create account
- `POST /api/login` - Login
- `POST /api/auth/forgot` - Request password reset
- `POST /api/auth/reset` - Reset password

### Leads
- `POST /api/leads/search` - Search leads (Firecrawl)
- `GET /api/leads` - Get user's leads

### Stats
- `GET /api/stats` - Get user stats

### Chat
- `POST /api/contact` - Submit chat message
- `GET /api/contact/responses` - Get bot responses
- `POST /api/chat/respond` - Save OpenClaw response

### Email
- `POST /api/emails/send` - Send email
- `GET /api/emails/sent` - Get sent emails

### Plans
- `GET /api/plans` - List available plans
- `POST /api/plans/upgrade` - Upgrade plan

## 📊 Plans

| Plan | Price | Leads | Emails | Campaigns |
|------|-------|-------|--------|-----------|
| Free | €0/mo | 10/mo | 50/mo | 1 |
| Starter | €29/mo | 100/mo | 500/mo | 5 |
| Pro | €79/mo | 500/mo | 2000/mo | 20 |
| Business | €149/mo | ∞ | ∞ | ∞ |

## 🔒 Security

- API keys in environment variables (never in code)
- JWT authentication
- CORS configured for production domains
- Password hashing
- Email verification codes (15 min expiry)

## 📝 Database Tables

- `users` - User accounts
- `plans` - Subscription plans
- `leads` - Saved leads
- `searches` - Search history
- `emails` - Sent emails
- `campaigns` - Email campaigns
- `chat_messages` - Chat interactions
- `password_resets` - Password reset codes

## 🤖 OpenClaw Integration

The chat widget connects to OpenClaw via Telegram bot:

1. User sends message from widget
2. Message saved to `chat_messages` (status: pending)
3. OpenClaw polls pending messages
4. OpenClaw generates response
5. Response saved via `/api/chat/respond`
6. Widget polls responses and displays

## 📜 License

Private - All rights reserved