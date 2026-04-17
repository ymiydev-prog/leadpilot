import type { InsforgeFunction } from '@insforge/sdk'
import { db, insert, select } from '../_shared/db'

export default async function handler(req: InsforgeFunction) {
  const url = new URL(req.url)
  const path = url.pathname.replace('/functions/', '')
  
  if (req.method === 'POST' && path === 'contact') {
    return handleContact(req)
  }
  
  if (req.method === 'GET' && path === 'contact/responses') {
    return handleResponses(req)
  }
  
  return new Response(JSON.stringify({ error: 'Not found' }), { 
    status: 404,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
  })
}

async function handleContact(req: InsforgeFunction) {
  try {
    const { name, email, company, message, source = 'contact_form' } = await req.json()
    
    const sessionId = crypto.randomUUID()
    
    await insert('contacts', {
      id: crypto.randomUUID(),
      name,
      email,
      company,
      message,
      source,
      status: 'new',
      received_at: new Date().toISOString()
    })
    
    await insert('chat_messages', {
      session_id: sessionId,
      user_name: name,
      user_email: email,
      user_message: message,
      source,
      status: 'pending',
      language: 'es'
    })
    
    return new Response(JSON.stringify({ 
      status: 'ok', 
      session_id: sessionId,
      message: 'Mensaje recibido'
    }), { 
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 })
  }
}

async function handleResponses(req: InsforgeFunction) {
  try {
    const sessionId = req.url.includes('session_id=') 
      ? new URL(req.url).searchParams.get('session_id')
      : null
    
    let rows: any[] = []
    
    if (sessionId) {
      rows = await select('chat_messages', { session_id: sessionId })
    } else {
      const { data, error } = await db.from('chat_messages')
        .select('*')
        .limit(50)
        .order('created_at', { ascending: false })
      rows = data || []
    }
    
    const responses = rows
      .filter(r => r.bot_response)
      .map(r => ({
        session_id: r.session_id,
        user_message: r.user_message,
        bot_response: r.bot_response,
        status: r.status,
        created_at: r.created_at
      }))
    
    return new Response(JSON.stringify({ responses }), { 
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500 })
  }
}
