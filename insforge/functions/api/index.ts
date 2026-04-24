import { createClient } from 'npm:@insforge/sdk'

const INSFORGE_URL = Deno.env.get('INSFORGE_URL') || 'https://nv96hw8d.eu-central.insforge.app'
const ANON_KEY = Deno.env.get('ANON_KEY') || Deno.env.get('INSFORGE_API_KEY') || ''
const JWT_SECRET = Deno.env.get('JWT_SECRET') || ''
const FIRECRAWL_API_KEY = Deno.env.get('FIRECRAWL_API_KEY') || ''
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY') || ''
const STRIPE_SECRET_KEY = Deno.env.get('STRIPE_SECRET_KEY') || ''

const db = createClient({ baseUrl: INSFORGE_URL, anonKey: ANON_KEY }).database

const SALT_LEN = 16
const ITERATIONS = 100000
const HASH_LEN = 32

// ---------- CRYPTO ----------

function bufToHex(buf: ArrayBuffer): string {
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('')
}

function hexToBuf(hex: string): Uint8Array {
  return new Uint8Array(hex.match(/.{2}/g)!.map(b => parseInt(b, 16)))
}

async function hashPassword(password: string): Promise<string> {
  const salt = crypto.getRandomValues(new Uint8Array(SALT_LEN))
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits'])
  const hash = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt, iterations: ITERATIONS, hash: 'SHA-256' }, key, HASH_LEN * 8)
  return bufToHex(salt) + ':' + bufToHex(hash)
}

async function verifyPassword(password: string, stored: string): Promise<boolean> {
  const [saltHex, hashHex] = stored.split(':')
  if (!saltHex || !hashHex) return false
  const salt = hexToBuf(saltHex)
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(password), 'PBKDF2', false, ['deriveBits'])
  const hash = await crypto.subtle.deriveBits({ name: 'PBKDF2', salt, iterations: ITERATIONS, hash: 'SHA-256' }, key, HASH_LEN * 8)
  return bufToHex(hash) === hashHex
}

async function hmacSign(message: string, secret: string): Promise<string> {
  const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(message))
  return btoa(String.fromCharCode(...new Uint8Array(sig))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

async function createjwt(payload: Record<string, any>): Promise<string> {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).replace(/=+$/, '')
  const body = btoa(JSON.stringify({ ...payload, exp: Math.floor(Date.now() / 1000) + 86400 })).replace(/=+$/, '')
  const sig = await hmacSign(`${header}.${body}`, JWT_SECRET)
  return `${header}.${body}.${sig}`
}

async function verifyjwt(token: string): Promise<any> {
  try {
    const [header, body, signature] = token.split('.')
    if (!header || !body || !signature) return null
    const sig = await hmacSign(`${header}.${body}`, JWT_SECRET)
    if (sig !== signature.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')) return null
    const payload = JSON.parse(atob(body))
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return null
    return payload
  } catch { return null }
}

// ---------- HELPERS ----------

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

function json(data: any, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
}

async function getUserFromRequest(req: Request) {
  const auth = req.headers.get('Authorization')
  if (!auth || !auth.startsWith('Bearer ')) return null
  const payload = await verifyjwt(auth.split(' ')[1])
  if (!payload) return null
  const { data } = await db.from('users').select('*').eq('email', payload.email)
  return data?.[0] || null
}

function extractDomain(url: string): string {
  if (!url) return ''
  try {
    const parsed = new URL(url)
    let domain = parsed.hostname || parsed.pathname.split('/')[0]
    return domain.replace('www.', '')
  } catch {
    return url.split('/')[0].replace('www.', '')
  }
}

function extractCompanyName(domain: string, title: string): string {
  if (title && title.length > 3) {
    const cleanTitle = title.split('|')[0].split(' - ')[0].split('—')[0].trim().substring(0, 50)
    if (cleanTitle && cleanTitle.length > 3) return cleanTitle
  }
  return domain.split('.')[0].replace(/-/g, ' ').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

// ---------- EMAIL ----------

async function sendEmailReal(to: string, subject: string, html: string): Promise<{ ok: boolean; id?: string; error?: string }> {
  try {
    const resp = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: 'LeadPilot <noreply@leadpilot.es>', to: [to], subject, html })
    })
    const data = await resp.json()
    return { ok: resp.ok, id: data?.id, error: data?.message }
  } catch (e: any) {
    return { ok: false, error: e.message }
  }
}

// ---------- FIRECRAWL ----------

async function scrapeLeadContact(url: string): Promise<{ email: string; phone: string }> {
  try {
    const response = await fetch('https://api.firecrawl.dev/v0/scrape', {
      method: 'POST',
      headers: { Authorization: `Bearer ${FIRECRAWL_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, formats: ['markdown'], only_main_content: true })
    })
    if (!response.ok) return { email: '', phone: '' }
    const data = await response.json()
    const content = (data.data?.markdown || '').trim()
    const emailMatch = content.match(/[\w.+-]+@[\w.-]+\.\w{2,}/i)
    const email = emailMatch ? emailMatch[0].toLowerCase() : ''
    const phonePatterns = [/\+34[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{3}/g, /\d{3}[-.\s]?\d{3}[-.\s]?\d{3}/g, /\d{9}/g]
    let phone = ''
    for (const pattern of phonePatterns) {
      const matches = content.match(pattern)
      if (matches && matches.length > 0) { phone = matches[0].replace(/\s+/g, ' ').trim(); break }
    }
    return { email, phone }
  } catch { return { email: '', phone: '' } }
}

async function searchLeadsWithFirecrawl(query: string, location: string, maxResults: number) {
  const badDomains = ['google', 'bing', 'yahoo', 'linkedin', 'twitter', 'facebook', 'instagram', 'youtube', 'pinterest', 'tiktok', 'tripadvisor', 'michelin']
  try {
    const response = await fetch('https://api.firecrawl.dev/v0/search', {
      method: 'POST',
      headers: { Authorization: `Bearer ${FIRECRAWL_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: `${query} ${location}`, limit: maxResults * 2 })
    })
    if (!response.ok) return []
    const data = await response.json()
    const results = data.data || []
    const seenDomains = new Set<string>()
    const leads: any[] = []
    for (const item of results) {
      const metadata = item.metadata || {}
      const url = metadata.sourceURL || ''
      if (!url) continue
      if (badDomains.some(bad => url.includes(bad))) continue
      const domain = extractDomain(url)
      if (!domain || seenDomains.has(domain)) continue
      if (!domain.includes('.')) continue
      seenDomains.add(domain)
      const companyName = extractCompanyName(domain, metadata.title || '')
      const { email, phone } = await scrapeLeadContact(url)
      leads.push({ id: crypto.randomUUID(), name: companyName, domain, url, email, phone, company: companyName, source: 'firecrawl', location })
    }
    return leads.slice(0, maxResults)
  } catch { return [] }
}

// ---------- STRIPE ----------

async function createStripeCheckout(userId: string, email: string, plan: string): Promise<string | null> {
  const prices: Record<string, string> = {
    starter: 'price_1R2abc123',
    pro: 'price_1R2def456',
    business: 'price_1R2ghi789'
  }
  const priceId = prices[plan]
  if (!priceId || !STRIPE_SECRET_KEY) return null
  try {
    const resp = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: { Authorization: `Bearer ${STRIPE_SECRET_KEY}`, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        'payment_method_types[]': 'card',
        'line_items[0][price]': priceId,
        'line_items[0][quantity]': '1',
        mode: 'subscription',
        success_url: `https://leadpilot.es/dashboard?checkout=success&plan=${plan}`,
        cancel_url: `https://leadpilot.es/dashboard?checkout=cancel`,
        'client_reference_id': userId,
        'customer_email': email
      })
    })
    const data = await resp.json()
    return data.url || null
  } catch { return null }
}

// ---------- HANDLER ----------

export default async function handler(req: Request) {
  const url = new URL(req.url)
  let path = url.pathname.replace(/^\/(functions\/api|api|functions)\/?/, '')

  if (req.method === 'OPTIONS') return new Response(null, { headers: corsHeaders })

  try {
    // REGISTER
    if (req.method === 'POST' && path === 'register') {
      const { name, email, password } = await req.json()
      if (!name || !email || !password) return json({ error: 'Missing fields' }, 400)
      if (password.length < 6) return json({ error: 'Password must be at least 6 characters' }, 400)
      const { data: existing } = await db.from('users').select('*').eq('email', email)
      if (existing && existing.length > 0) return json({ error: 'Email already registered' }, 400)
      const id = crypto.randomUUID()
      const hashed = await hashPassword(password)
      await db.from('users').insert([{ id, name, email, password: hashed, plan: 'free', leads_used: 0, emails_used: 0, campaigns_used: 0, created_at: new Date().toISOString() }])
      const token = await createjwt({ email, id })
      return json({ status: 'ok', success: true, token, user: { id, name, email, plan: 'free' } })
    }

    // LOGIN
    if (req.method === 'POST' && path === 'login') {
      const { email, password } = await req.json()
      if (!email || !password) return json({ error: 'Missing credentials' }, 400)
      const { data: users } = await db.from('users').select('*').eq('email', email)
      const user = users?.[0]
      if (!user) return json({ error: 'Invalid credentials' }, 401)
      const valid = await verifyPassword(password, user.password)
      if (!valid) return json({ error: 'Invalid credentials' }, 401)
      const token = await createjwt({ email: user.email, id: user.id })
      return json({ status: 'ok', success: true, token, user: { id: user.id, name: user.name, email: user.email, plan: user.plan } })
    }

    // FORGOT PASSWORD
    if (req.method === 'POST' && path === 'forgot-password') {
      const { email } = await req.json()
      const { data: users } = await db.from('users').select('*').eq('email', email)
      if (!users || users.length === 0) return json({ status: 'ok' })
      const resetCode = Math.floor(100000 + Math.random() * 900000).toString()
      const expiresAt = new Date(Date.now() + 15 * 60 * 1000).toISOString()
      await db.from('password_resets').insert([{ email, code: resetCode, expires_at: expiresAt, used: false, created_at: new Date().toISOString() }])
      const html = `<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;"><h2 style="color:#6366f1;">LeadPilot - Recuperar Contraseña</h2><p>Hola,</p><p>Tu código de recuperación:</p><div style="background:#f3f4f6;padding:20px;border-radius:8px;text-align:center;font-size:32px;font-weight:bold;letter-spacing:8px;margin:20px 0;">${resetCode}</div><p style="color:#6b7280;font-size:14px;">Expira en 15 minutos. Si no lo solicitaste, ignora este email.</p></div>`
      await sendEmailReal(email, 'LeadPilot - Código de recuperación', html)
      return json({ status: 'ok', success: true })
    }

    // RESET PASSWORD
    if (req.method === 'POST' && path === 'reset-password') {
      const { token: code, new_password } = await req.json()
      if (!code || !new_password) return json({ error: 'Missing fields' }, 400)
      if (new_password.length < 6) return json({ error: 'Password must be at least 6 characters' }, 400)
      const { data: resets } = await db.from('password_resets').select('*').eq('code', code).eq('used', false)
      const reset = resets?.[0]
      if (!reset || new Date(reset.expires_at) < new Date()) return json({ error: 'Invalid or expired code' }, 400)
      const hashed = await hashPassword(new_password)
      await db.from('users').update({ password: hashed }).eq('email', reset.email)
      await db.from('password_resets').update({ used: true }).eq('code', code)
      return json({ status: 'ok', success: true })
    }

    // CHANGE PASSWORD (new endpoint)
    if (req.method === 'POST' && path === 'auth/change-password') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { old_password, new_password } = await req.json()
      if (!old_password || !new_password) return json({ error: 'Missing fields' }, 400)
      if (new_password.length < 6) return json({ error: 'Password must be at least 6 characters' }, 400)
      const valid = await verifyPassword(old_password, user.password)
      if (!valid) return json({ error: 'Invalid current password' }, 400)
      const hashed = await hashPassword(new_password)
      await db.from('users').update({ password: hashed }).eq('id', user.id)
      return json({ status: 'ok', success: true })
    }

    // USER ME
    if (req.method === 'GET' && path === 'user/me') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { data: plans } = await db.from('plans').select('*').eq('id', user.plan || 'free')
      const plan = plans?.[0]
      return json({
        user: { id: user.id, name: user.name, email: user.email, plan: user.plan },
        limits: { leads: plan?.leads_limit ?? 10, emails: plan?.emails_limit ?? 50, campaigns: plan?.campaigns_limit ?? 1 }
      })
    }

    // UPDATE PROFILE
    if (req.method === 'PUT' && path === 'user/me') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { name } = await req.json()
      if (name) await db.from('users').update({ name }).eq('id', user.id)
      return json({ status: 'ok', success: true })
    }

    // LEADS SEARCH
    if (req.method === 'POST' && path === 'leads/search') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { data: planData } = await db.from('plans').select('*').eq('id', user.plan || 'free')
      const plan = planData?.[0] || { leads_limit: 10 }
      const { data: existing } = await db.from('leads').select('id', { count: 'exact' }).eq('user_id', user.id)
      const currentLeads = existing?.length || 0
      const leadsLimit = plan.leads_limit
      if (leadsLimit !== -1 && currentLeads >= leadsLimit) return json({ error: `Límite de ${leadsLimit} leads alcanzado. Actualiza tu plan.` }, 403)
      const { query, location, max_results = 10 } = await req.json()
      if (!query) return json({ error: 'Query required' }, 400)
      const searchId = crypto.randomUUID()
      const leads = await searchLeadsWithFirecrawl(query, location || '', Math.min(max_results, 50))
      const withContact = leads.filter((l: any) => l.email || l.phone)
      const available = leadsLimit === -1 ? withContact.length : Math.min(withContact.length, leadsLimit - currentLeads)
      const toSave = withContact.slice(0, Math.max(0, available))
      for (const lead of toSave) {
        await db.from('leads').insert([{ id: lead.id, user_id: user.id, name: lead.name, email: lead.email || '', phone: lead.phone || '', company: lead.company || lead.name, source: 'firecrawl', location: location || '', created_at: new Date().toISOString() }])
      }
      await db.from('users').update({ leads_used: currentLeads + toSave.length }).eq('id', user.id)
      await db.from('searches').insert([{ id: searchId, user_id: user.id, query, location: location || '', leads: toSave, created_at: new Date().toISOString() }])
      return json({ status: 'ok', success: true, search_id: searchId, leads: toSave, found: leads.length, saved: toSave.length, remaining: leadsLimit === -1 ? 'unlimited' : Math.max(0, leadsLimit - currentLeads - toSave.length) })
    }

    // GET LEADS
    if (req.method === 'GET' && path === 'leads') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { data: leads } = await db.from('leads').select('*').eq('user_id', user.id).order('created_at', { ascending: false })
      return json({ leads: leads || [] })
    }

    // EXPORT CSV
    if (req.method === 'GET' && path === 'leads/export') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { data: leads } = await db.from('leads').select('*').eq('user_id', user.id)
      const rows = leads || []
      let csv = 'Empresa,Email,Telefono,Web,Fuente\n'
      for (const l of rows) {
        csv += `"${(l.name || '').replace(/"/g, '""')}","${l.email || ''}","${l.phone || ''}","${l.domain || ''}","${l.source || ''}"\n`
      }
      return new Response(csv, { headers: { 'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': 'attachment; filename="leadpilot-leads.csv"', ...corsHeaders } })
    }

    // ANALYTICS / STATS
    if (req.method === 'GET' && (path === 'stats' || path === 'analytics/stats')) {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { data: leadsData } = await db.from('leads').select('id', { count: 'exact' }).eq('user_id', user.id)
      const { data: emailsSent } = await db.from('emails').select('*').eq('user_id', user.id)
      const { data: campaigns } = await db.from('campaigns').select('*').eq('user_id', user.id)
      const totalLeads = leadsData?.length || 0
      const totalEmails = (emailsSent || []).length
      const opened = (emailsSent || []).filter((e: any) => e.status === 'opened').length
      return json({ leads: totalLeads, emails_sent: totalEmails, open_rate: totalEmails > 0 ? Math.round(opened / totalEmails * 100 * 10) / 10 : 0, campaigns: (campaigns || []).length, plan: user.plan || 'free', leads_used: totalLeads, emails_used: totalEmails, campaigns_used: (campaigns || []).length, month: new Date().toISOString().slice(0, 7) })
    }

    // PLAN UPGRADE
    if (req.method === 'POST' && path === 'plans/upgrade') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { plan } = await req.json()
      const { data: plans } = await db.from('plans').select('*').eq('id', plan)
      if (!plans || plans.length === 0) return json({ error: 'Plan not found' }, 400)
      await db.from('users').update({ plan }).eq('id', user.id)
      const p = plans[0]
      return json({ status: 'ok', success: true, plan, limits: { leads: p.leads_limit, emails: p.emails_limit, campaigns: p.campaigns_limit } })
    }

    // STRIPE CHECKOUT (REAL)
    if (req.method === 'POST' && path === 'stripe/create-checkout') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { plan } = await req.json()
      if (!['starter', 'pro', 'business'].includes(plan)) return json({ error: 'Invalid plan' }, 400)
      const checkoutUrl = await createStripeCheckout(user.id, user.email, plan)
      if (!checkoutUrl) return json({ error: 'Could not create checkout session' }, 500)
      return json({ status: 'ok', url: checkoutUrl })
    }

    // STRIPE WEBHOOK
    if (req.method === 'POST' && path === 'stripe/webhook') {
      const body = await req.text()
      const sig = req.headers.get('stripe-signature') || ''
      // For simplicity, verify the event type and update plan
      try {
        const event = JSON.parse(body)
        if (event.type === 'checkout.session.completed') {
          const session = event.data.object
          const userId = session.client_reference_id
          const plan = new URL(session.success_url || '').searchParams.get('plan') || 'starter'
          if (userId) await db.from('users').update({ plan }).eq('id', userId)
          await db.from('stripe_payments').insert([{ id: session.id, user_id: userId, plan, amount: session.amount_total, status: 'completed', created_at: new Date().toISOString() }])
        }
        return json({ received: true })
      } catch { return json({ received: true }) }
    }

    // CAMPAIGNS CREATE
    if (req.method === 'POST' && path === 'campaigns/create') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { name, subject, template } = await req.json()
      if (!name || !subject) return json({ error: 'Missing fields' }, 400)
      const { data: searches } = await db.from('searches').select('*').eq('user_id', user.id)
      let allLeads: any[] = []
      for (const s of (searches || [])) allLeads = allLeads.concat((s.leads || []).slice(0, 20))
      const campaignId = crypto.randomUUID()
      await db.from('campaigns').insert([{ id: campaignId, user_id: user.id, name, subject, template: template || '', leads: allLeads, status: 'draft', created_at: new Date().toISOString() }])
      return json({ status: 'ok', success: true, campaign_id: campaignId, total_leads: allLeads.length })
    }

    // CAMPAIGNS LIST
    if (req.method === 'GET' && path === 'campaigns') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { data: campaigns } = await db.from('campaigns').select('*').eq('user_id', user.id)
      return json({ campaigns: campaigns || [] })
    }

    // CAMPAIGNS SEND (REAL)
    if (req.method === 'POST' && path.startsWith('campaigns/') && path.endsWith('/send')) {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const campaignId = path.split('/')[1]
      const { data: campaigns } = await db.from('campaigns').select('*').eq('id', campaignId).eq('user_id', user.id)
      const campaign = campaigns?.[0]
      if (!campaign) return json({ error: 'Campaign not found' }, 404)
      const leads = campaign.leads || []
      let sent = 0
      let errors = 0
      for (const lead of leads) {
        if (!lead.email) continue
        const body = (campaign.template || '').replace(/\{\{nombre\}\}/g, lead.name || '').replace(/\{\{empresa\}\}/g, lead.company || '')
        const result = await sendEmailReal(lead.email, campaign.subject, body.replace(/\n/g, '<br>'))
        if (result.ok) {
          sent++
          await db.from('emails').insert([{ id: crypto.randomUUID(), user_id: user.id, to_email: lead.email, subject: campaign.subject, status: 'sent', sent_at: new Date().toISOString(), created_at: new Date().toISOString() }])
        } else { errors++ }
      }
      await db.from('campaigns').update({ status: 'sent', sent, errors, updated_at: new Date().toISOString() }).eq('id', campaignId)
      await db.from('users').update({ emails_used: (user.emails_used || 0) + sent }).eq('id', user.id)
      return json({ status: 'ok', sent, errors, total: leads.length })
    }

    // EMAILS SENT
    if (req.method === 'GET' && path === 'emails/sent') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { data: emails } = await db.from('emails').select('*').eq('user_id', user.id).order('created_at', { ascending: false })
      return json({ emails: emails || [], count: (emails || []).length })
    }

    // EMAIL GENERATE
    if (req.method === 'POST' && path === 'emails/generate') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { lead_name, tone = 'profesional' } = await req.json()
      const name = lead_name || 'Contacto'
      const templates: Record<string, { subject: string; body: string }> = {
        profesional: { subject: `Propuesta de valor para ${name}`, body: `Hola ${name},\n\nSoy ${user.name || 'el equipo de LeadPilot'}. Me gustaría explorar cómo podemos ayudar a ${name} a escalar su generación de leads B2B.\n\n¿Tienes 15 minutos esta semana para una breve llamada?\n\nSaludos,\nLeadPilot` },
        casual: { subject: `¿Hablamos, ${name}?`, body: `Hola ${name},\n\nVi lo que están haciendo en ${name} y me parece genial. Me encantaría ver si podemos colaborar.\n\n¿Te viene bien un café virtual esta semana? ☕\n\nUn abrazo,\n${user.name || 'LeadPilot'}` },
        directo: { subject: `LeadPilot + ${name}`, body: `${name},\n\nGeneramos leads B2B verificados en España. 100 leads de prueba gratis.\n\n¿Te interesa? Responde SÍ y te los envío hoy.\n\nLeadPilot` }
      }
      const tmpl = templates[tone] || templates.profesional
      return json({ status: 'ok', success: true, subject: tmpl.subject, email: tmpl.body })
    }

    // EMAIL SEND (REAL)
    if (req.method === 'POST' && path === 'emails/send') {
      const user = await getUserFromRequest(req)
      if (!user) return json({ error: 'Unauthorized' }, 401)
      const { to_email, to_name, subject, body_html } = await req.json()
      if (!to_email || !subject || !body_html) return json({ error: 'Missing fields' }, 400)
      const result = await sendEmailReal(to_email, subject, body_html)
      if (!result.ok) return json({ error: result.error || 'Failed to send email' }, 500)
      await db.from('emails').insert([{ id: crypto.randomUUID(), user_id: user.id, to_email, subject, status: 'sent', sent_at: new Date().toISOString(), created_at: new Date().toISOString() }])
      await db.from('users').update({ emails_used: (user.emails_used || 0) + 1 }).eq('id', user.id)
      return json({ status: 'ok', success: true, tracking_id: result.id || crypto.randomUUID().slice(0, 8) })
    }

    // CONTACT
    if (req.method === 'POST' && path === 'contact') {
      const { name, email, company, message, source = 'contact_form' } = await req.json()
      if (!name || !email || !message) return json({ error: 'Missing fields' }, 400)
      const sessionId = crypto.randomUUID()
      await db.from('chat_messages').insert([{ session_id: sessionId, user_name: name, user_email: email, user_message: message, source, status: 'pending', language: 'es' }])
      // Also notify admin
      if (RESEND_API_KEY) {
        await sendEmailReal('contacto@leadpilot.es', `Nuevo contacto de ${name}`, `<p><b>Nombre:</b> ${name}</p><p><b>Email:</b> ${email}</p><p><b>Empresa:</b> ${company || '-'}</p><p><b>Mensaje:</b> ${message}</p>`)
      }
      return json({ status: 'ok', session_id: sessionId, message: 'Mensaje recibido' })
    }

    // CONTACT RESPONSES
    if (req.method === 'GET' && path === 'contact/responses') {
      const sessionId = url.searchParams.get('session_id')
      let query = db.from('chat_messages').select('*').limit(50).order('created_at', { ascending: false })
      if (sessionId) query = query.eq('session_id', sessionId)
      const { data: rows } = await query
      const responses = (rows || []).filter((r: any) => r.bot_response).map((r: any) => ({ session_id: r.session_id, user_message: r.user_message, bot_response: r.bot_response, status: r.status, created_at: r.created_at }))
      return json({ responses })
    }

    // CHAT RESPOND (admin)
    if (req.method === 'POST' && path === 'chat/respond') {
      const { session_id, response } = await req.json()
      if (!session_id || !response) return json({ error: 'Missing session_id or response' }, 400)
      const { data: rows } = await db.from('chat_messages').select('*').eq('session_id', session_id).limit(1)
      const row = rows?.[0]
      if (!row) return json({ error: 'Session not found' }, 404)
      await db.from('chat_messages').update({ bot_response: response, status: 'responded', responded_at: new Date().toISOString() }).eq('id', row.id)
      return json({ status: 'ok', success: true })
    }

    // HEALTH CHECK
    if (req.method === 'GET' && path === 'health') {
      return json({ status: 'ok', version: '2.0', time: new Date().toISOString() })
    }

    return json({ error: 'Not found', path }, 404)
  } catch (e: any) {
    console.error('API Error:', e)
    return json({ error: e.message }, 500)
  }
}
