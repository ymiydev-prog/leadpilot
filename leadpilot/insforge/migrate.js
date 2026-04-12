// LeadPilot + InsForge Integration
// Replace JSON files with InsForge database

const API_KEY = "ik_35c9fe063dc416d6bb3a636dc44b067c"
const BASE_URL = "https://nv96hw8d.eu-central.insforge.app"

// Helper function for API calls
async function insforge(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`
  const response = await fetch(url, {
    ...options,
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  })
  return response.json()
}

// Users
export const users = {
  async create(email, password, name) {
    return insforge('/api/database/records/users', {
      method: 'POST',
      headers: { 'Prefer': 'return=representation' },
      body: JSON.stringify([{ email, password, name }])
    })
  },
  
  async findByEmail(email) {
    const data = await insforge(`/api/database/records/users?email=eq.${encodeURIComponent(email)}`)
    return data[0] || null
  },
  
  async update(id, updates) {
    return insforge(`/api/database/records/users?id=eq.${id}`, {
      method: 'PATCH',
      headers: { 'Prefer': 'return=representation' },
      body: JSON.stringify([updates])
    })
  },
  
  async getLimits(id) {
    const data = await insforge(`/api/database/records/users?id=eq.${id}&select=leads_used,leads_limit,plan`)
    return data[0] || null
  }
}

// Leads
export const leads = {
  async create(lead) {
    return insforge('/api/database/records/leads', {
      method: 'POST',
      headers: { 'Prefer': 'return=representation' },
      body: JSON.stringify([lead])
    })
  },
  
  async findByUser(userId) {
    return insforge(`/api/database/records/leads?user_id=eq.${userId}&order=created_at.desc`)
  },
  
  async count(userId) {
    const data = await insforge(`/api/database/records/leads?user_id=eq.${userId}`)
    return data.length
  },
  
  async delete(id) {
    return insforge(`/api/database/records/leads?id=eq.${id}`, { method: 'DELETE' })
  }
}

// Campaigns
export const campaigns = {
  async create(campaign) {
    return insforge('/api/database/records/campaigns', {
      method: 'POST',
      headers: { 'Prefer': 'return=representation' },
      body: JSON.stringify([campaign])
    })
  },
  
  async findByUser(userId) {
    return insforge(`/api/database/records/campaigns?user_id=eq.${userId}&order=created_at.desc`)
  },
  
  async update(id, updates) {
    return insforge(`/api/database/records/campaigns?id=eq.${id}`, {
      method: 'PATCH',
      headers: { 'Prefer': 'return=representation' },
      body: JSON.stringify([updates])
    })
  }
}

export default { users, leads, campaigns }
