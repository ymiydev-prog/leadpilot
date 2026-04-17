import { createClient } from 'npm:@insforge/sdk'

const INSFORGE_URL = 'https://nv96hw8d.eu-central.insforge.app'
const ANON_KEY = 'ik_35c9fe063dc416d6bb3a636dc44b067c'
const JWT_SECRET = 'o87LW7uuLXBOxUhOz5Ib/c84+JLkat8QfUsDXPJWtUg='

const FIRECRAWL_API_KEY = Deno.env.get('FIRECRAWL_API_KEY') || 'fc-7d9a7bd9c81346dfbfba5c7d55743bd5'

const db = createClient({
  baseUrl: INSFORGE_URL,
  anonKey: ANON_KEY
})

const database = db.database

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
    if (cleanTitle && cleanTitle.length > 3) {
      return cleanTitle
    }
  }
  return domain.split('.')[0].replace(/-/g, ' ').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

async function scrapeLeadContact(url: string): Promise<{email: string, phone: string}> {
  try {
    const response = await fetch('https://api.firecrawl.dev/v0/scrape', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${FIRECRAWL_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: url,
        formats: ['markdown'],
        only_main_content: true
      })
    })
    
    if (!response.ok) {
      console.error('Firecrawl scrape error:', response.status)
      return { email: '', phone: '' }
    }
    
    const data = await response.json()
    const content = (data.data?.markdown || '').trim()
    
    let email = ''
    let phone = ''
    
    const emailMatch = content.match(/[\w.+-]+@[\w.-]+\.\w{2,}/i)
    if (emailMatch) email = emailMatch[0].toLowerCase()
    
    const phonePatterns = [
      /\+34[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{3}/g,
      /\d{3}[-.\s]?\d{3}[-.\s]?\d{3}/g,
      /\d{9}/g
    ]
    
    for (const pattern of phonePatterns) {
      const matches = content.match(pattern)
      if (matches && matches.length > 0) {
        phone = matches[0].replace(/\s+/g, ' ').trim()
        break
      }
    }
    
    return { email, phone }
  } catch (e) {
    console.error('Scrape error:', e)
    return { email: '', phone: '' }
  }
}

async function searchLeadsWithFirecrawl(query: string, location: string, maxResults: number) {
  const searchQuery = `${query} ${location}`
  const badDomains = ['google', 'bing', 'yahoo', 'linkedin', 'twitter', 'facebook', 'instagram', 'youtube', 'pinterest', 'tiktok', 'tripadvisor', 'michelin']
  
  try {
    const response = await fetch('https://api.firecrawl.dev/v0/search', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${FIRECRAWL_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query: searchQuery, limit: maxResults })
    })
    
    if (!response.ok) {
      console.error('Firecrawl error:', response.status)
      return []
    }
    
    const data = await response.json()
    const results = data.data || []
    const seenDomains = new Set<string>()
    const leads = []
    
    for (const item of results) {
      const metadata = item.metadata || {}
      const url = metadata.sourceURL || ''
      
      if (!url) continue
      
      if (badDomains.some(bad => url.includes(bad))) continue
      
      const domain = extractDomain(url)
      if (!domain || domain.includes('www.' + domain) || seenDomains.has(domain)) continue
      if (!domain.includes('.')) continue
      
      seenDomains.add(domain)
      
      const companyName = extractCompanyName(domain, metadata.title || '')
      
      const { email, phone } = await scrapeLeadContact(url)
      
      leads.push({
        id: crypto.randomUUID(),
        name: companyName,
        domain: domain,
        url: url,
        email: email,
        phone: phone,
        company: companyName,
        source: 'firecrawl',
        location: location
      })
    }
    
    return leads.slice(0, maxResults)
  } catch (e) {
    console.error('Firecrawl error:', e)
    return []
  }
}

function hashPassword(password: string): string {
  let hash = 0
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash).toString(16).padStart(8, '0')
}

function createjwt(payload: any): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const exp = Math.floor(Date.now() / 1000) + 86400
  const body = btoa(JSON.stringify({ ...payload, exp }))
  const signature = btoa(`${header}.${body}.${JWT_SECRET}`)
  return `${header}.${body}.${signature}`
}

function verifyjwt(token: string): any {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const [header, body, signature] = parts
    const expectedSig = btoa(`${header}.${body}.${JWT_SECRET}`)
    if (signature !== expectedSig) return null
    return JSON.parse(atob(body))
  } catch {
    return null
  }
}

async function getUserFromRequest(req: Request) {
  const auth = req.headers.get('Authorization')
  if (!auth || !auth.startsWith('Bearer ')) return null
  const token = auth.split(' ')[1]
  const payload = verifyjwt(token)
  if (!payload) return null
  const { data } = await database.from('users').select('*').eq('email', payload.email)
  return data?.[0] || null
}

async function sendEmail(to: string, subject: string, html: string) {
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('RESEND_API_KEY')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'LeadPilot <noreply@leadpilot.es>',
        to: [to],
        subject: subject,
        html: html
      })
    })
    const data = await response.json()
    console.log('Resend response:', data)
    return response.ok
  } catch (e) {
    console.error('Email error:', e)
    return false
  }
}

export default async function handler(req: Request) {
  const url = new URL(req.url)
  let path = url.pathname
  path = path.replace('/functions/api/', '').replace('/api/', '').replace('/functions/', '').replace('/api', '')
  if (!path || path === url.pathname) {
    path = path.split('/').filter(Boolean).join('/') || '/'
  }
  
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  }

  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    if (req.method === 'POST' && path === 'register') {
      const { name, email, password } = await req.json()
      if (!name || !email || !password) {
        return new Response(JSON.stringify({ error: 'Missing fields' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      const { data: existing } = await database.from('users').select('*').eq('email', email)
      if (existing && existing.length > 0) {
        return new Response(JSON.stringify({ error: 'Email already registered' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      const id = crypto.randomUUID()
      await database.from('users').insert([{
        id,
        name,
        email,
        password: hashPassword(password),
        plan: 'free',
        leads_used: 0,
        emails_used: 0,
        campaigns_used: 0,
        created_at: new Date().toISOString()
      }])
      const token = createjwt({ email, id })
      return new Response(JSON.stringify({ status: 'ok', success: true, token, user: { id, name, email, plan: 'free' } }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    if (req.method === 'POST' && path === 'login') {
      const { email, password } = await req.json()
      if (!email || !password) {
        return new Response(JSON.stringify({ error: 'Missing credentials' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      const { data: users } = await database.from('users').select('*').eq('email', email)
      const user = users?.[0]
      if (!user || user.password !== hashPassword(password)) {
        return new Response(JSON.stringify({ error: 'Invalid credentials' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      const token = createjwt({ email: user.email, id: user.id })
      return new Response(JSON.stringify({ status: 'ok', success: true, token, user: { id: user.id, name: user.name, email: user.email, plan: user.plan } }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    if (req.method === 'POST' && path === 'auth/forgot') {
      const { email } = await req.json()
      const { data: users } = await database.from('users').select('*').eq('email', email)
      if (!users || users.length === 0) {
        return new Response(JSON.stringify({ status: 'ok' }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      const resetCode = Math.floor(100000 + Math.random() * 900000).toString()
      const expiresAt = new Date(Date.now() + 15 * 60 * 1000).toISOString()
      
      await database.from('password_resets').insert([{
        email,
        code: resetCode,
        expires_at: expiresAt,
        used: false,
        created_at: new Date().toISOString()
      }])
      
      const htmlContent = `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #6366f1;">LeadPilot - Recuperar Contraseña</h2>
          <p>Hola,</p>
          <p>Has solicitado recuperar tu contraseña. Usa el siguiente código:</p>
          <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; font-size: 32px; font-weight: bold; letter-spacing: 8px; margin: 20px 0;">
            ${resetCode}
          </div>
          <p style="color: #6b7280; font-size: 14px;">Este código expira en 15 minutos.</p>
          <p style="color: #6b7280; font-size: 14px;">Si no solicitaste este código, ignora este email.</p>
        </div>
      `
      
      const sent = await sendEmail(email, 'LeadPilot - Código de recuperación', htmlContent)
      
      return new Response(JSON.stringify({ status: 'ok', sent }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'auth/reset') {
      const { code, new_password } = await req.json()
      const { data: resets } = await database.from('password_resets').select('*').eq('code', code).eq('used', false)
      const reset = resets?.[0]
      
      if (!reset || new Date(reset.expires_at) < new Date()) {
        return new Response(JSON.stringify({ error: 'Invalid or expired code' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      
      await database.from('users').update({ password: hashPassword(new_password) }).eq('email', reset.email)
      await database.from('password_resets').update({ used: true }).eq('code', code)
      
      return new Response(JSON.stringify({ status: 'ok', success: true }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'GET' && path === 'user/me') {
      const user = await getUserFromRequest(req)
      if (!user) {
        return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      return new Response(JSON.stringify({ user: { id: user.id, name: user.name, email: user.email, plan: user.plan } }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    if (req.method === 'POST' && path === 'leads/search') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      
      const { data: planData } = await database.from('plans').select('*').eq('id', user.plan || 'free')
      const plan = planData?.[0] || { leads_limit: 10, emails_limit: 50, campaigns_limit: 1 }
      
      const { data: existingLeads } = await database.from('leads').select('id', { count: 'exact' }).eq('user_id', user.id)
      const currentLeads = existingLeads?.length || 0
      const leadsLimit = plan.leads_limit
      
      if (leadsLimit !== -1 && currentLeads >= leadsLimit) {
        return new Response(JSON.stringify({ error: `Has alcanzado el límite de ${leadsLimit} leads de tu plan ${user.plan || 'free'}. Actualiza tu plan para más leads.` }), { status: 403, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      
      const { query, location, max_results = 10 } = await req.json()
      const searchId = crypto.randomUUID()
      
      let leads = await searchLeadsWithFirecrawl(query, location || '', Math.min(max_results, 50))
      
      const leadsWithContact = leads.filter(l => l.email || l.phone)
      const leadsWithoutContact = leads.filter(l => !l.email && !l.phone)
      
      const availableSlots = leadsLimit === -1 ? leadsWithContact.length : Math.min(leadsWithContact.length, leadsLimit - currentLeads)
      const leadsToSave = leadsWithContact.slice(0, Math.max(0, availableSlots))
      
      for (const lead of leadsToSave) {
        await database.from('leads').insert([{
          id: lead.id,
          user_id: user.id,
          name: lead.name,
          email: lead.email || '',
          phone: lead.phone || '',
          company: lead.company || lead.name,
          source: 'firecrawl',
          location: location || '',
          created_at: new Date().toISOString()
        }])
      }
      
      const newLeadsCount = leadsToSave.length
      await database.from('users').update({ leads_used: currentLeads + newLeadsCount }).eq('id', user.id)
      
      await database.from('searches').insert([{
        id: searchId,
        user_id: user.id,
        query,
        location: location || '',
        leads: leadsToSave,
        created_at: new Date().toISOString()
      }])
      
      const response: any = {
        status: 'ok',
        success: true,
        search_id: searchId,
        leads: leadsToSave,
        found: leads.length,
        with_contact: leadsWithContact.length,
        without_contact: leadsWithoutContact.length,
        saved: leadsToSave.length,
        remaining: leadsLimit === -1 ? 'unlimited' : Math.max(0, leadsLimit - currentLeads - leadsToSave.length)
      }
      
      return new Response(JSON.stringify(response), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'GET' && path === 'leads') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { data: leads } = await database.from('leads').select('*').eq('user_id', user.id).order('created_at', { ascending: false })
      return new Response(JSON.stringify({ leads: leads || [] }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'GET' && (path === 'stats' || path === 'analytics/stats')) {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { data: leadsData } = await database.from('leads').select('id', { count: 'exact' }).eq('user_id', user.id)
      const { data: emailsSent } = await database.from('emails').select('*').eq('user_id', user.id)
      const { data: campaigns } = await database.from('campaigns').select('*').eq('user_id', user.id)
      const totalLeads = leadsData?.length || 0
      const totalEmails = (emailsSent || []).length
      const opened = (emailsSent || []).filter((e: any) => e.status === 'opened').length
      return new Response(JSON.stringify({
        leads: totalLeads,
        emails_sent: totalEmails,
        open_rate: totalEmails > 0 ? Math.round(opened / totalEmails * 100 * 10) / 10 : 0,
        campaigns: (campaigns || []).length,
        plan: user.plan || 'free',
        leads_used: totalLeads,
        emails_used: totalEmails,
        campaigns_used: (campaigns || []).length,
        month: new Date().toISOString().slice(0, 7)
      }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'plans/upgrade') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { plan } = await req.json()
      const { data: plans } = await database.from('plans').select('*').eq('id', plan)
      if (!plans || plans.length === 0) {
        return new Response(JSON.stringify({ error: 'Plan not found' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
      await database.from('users').update({ plan }).eq('id', user.id)
      const planData = plans[0]
      return new Response(JSON.stringify({
        status: 'ok', success: true, plan,
        limits: { leads: planData.leads_limit, emails: planData.emails_limit, campaigns: planData.campaigns_limit }
      }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'stripe/create-checkout') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      return new Response(JSON.stringify({ url: 'https://checkout.stripe.com', status: 'ok' }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'campaigns/create') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { name, subject, template } = await req.json()
      const { data: searches } = await database.from('searches').select('*').eq('user_id', user.id)
      let allLeads: any[] = []
      for (const s of (searches || [])) {
        allLeads = allLeads.concat((s.leads || []).slice(0, 20))
      }
      const campaignId = crypto.randomUUID()
      await database.from('campaigns').insert([{
        id: campaignId,
        user_id: user.id,
        name,
        subject,
        template: template || '',
        leads: allLeads,
        status: 'draft',
        created_at: new Date().toISOString()
      }])
      return new Response(JSON.stringify({ status: 'ok', success: true, campaign_id: campaignId, total_leads: allLeads.length }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    if (req.method === 'GET' && path === 'campaigns') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { data: campaigns } = await database.from('campaigns').select('*').eq('user_id', user.id)
      return new Response(JSON.stringify({ campaigns: campaigns || {} }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'campaigns/send') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      return new Response(JSON.stringify({ status: 'ok', sent: 0, errors: 0 }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'GET' && path === 'emails/sent') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { data: emails } = await database.from('emails').select('*').eq('user_id', user.id)
      return new Response(JSON.stringify({ emails: emails || {}, count: (emails || []).length }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'emails/generate') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { lead_name } = await req.json()
      return new Response(JSON.stringify({
        status: 'ok', success: true,
        subject: `Introducción para ${lead_name}`,
        body: `Hola ${lead_name},\n\nMe gustaría conectar contigo...`
      }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'emails/send') {
      const user = await getUserFromRequest(req)
      if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      const { to_email, to_name, subject, body_html } = await req.json()
      await database.from('emails').insert([{
        id: crypto.randomUUID(),
        user_id: user.id,
        to_email,
        subject,
        status: 'sent',
        sent_at: new Date().toISOString(),
        created_at: new Date().toISOString()
      }])
      return new Response(JSON.stringify({ status: 'ok', success: true, tracking_id: crypto.randomUUID().slice(0, 8) }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    if (req.method === 'POST' && path === 'contact') {
      const { name, email, company, message, source = 'contact_form' } = await req.json()
      const sessionId = crypto.randomUUID()
      await database.from('chat_messages').insert([{
        session_id: sessionId,
        user_name: name,
        user_email: email,
        user_message: message,
        source,
        status: 'pending',
        language: 'es'
      }])
      return new Response(JSON.stringify({ status: 'ok', session_id: sessionId, message: 'Mensaje recibido' }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      })
    }

    if (req.method === 'GET' && path === 'contact/responses') {
      const sessionId = url.searchParams.get('session_id')
      let query = database.from('chat_messages').select('*').limit(50).order('created_at', { ascending: false })
      if (sessionId) {
        query = query.eq('session_id', sessionId)
      }
      const { data: rows } = await query
      const responses = (rows || []).filter((r: any) => r.bot_response).map((r: any) => ({
        session_id: r.session_id,
        user_message: r.user_message,
        bot_response: r.bot_response,
        status: r.status,
        created_at: r.created_at
      }))
      return new Response(JSON.stringify({ responses }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
    }

    if (req.method === 'POST' && path === 'chat/respond') {
      try {
        const { session_id, response } = await req.json()
        if (!session_id || !response) {
          return new Response(JSON.stringify({ error: 'Missing session_id or response' }), { status: 400, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
        }
        
        const { data: rows } = await database.from('chat_messages').select('*').eq('session_id', session_id).limit(1)
        const row = rows?.[0]
        
        if (!row) {
          return new Response(JSON.stringify({ error: 'Session not found' }), { status: 404, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
        }
        
        await database.from('chat_messages').update({
          bot_response: response,
          status: 'responded',
          responded_at: new Date().toISOString()
        }).eq('id', row.id)
        
        return new Response(JSON.stringify({ status: 'ok', success: true }), { headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      } catch (e: any) {
        return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
      }
    }

    return new Response(JSON.stringify({ error: 'Not found', path }), { status: 404, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
  } catch (e: any) {
    console.error('API Error:', e)
    return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...corsHeaders } })
  }
}
