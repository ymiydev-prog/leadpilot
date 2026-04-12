// InsForge Client for LeadPilot
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: 'https://nv96hw8d.eu-central.insforge.app',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3OC0xMjM0LTU2NzgtOTBhYi1jZGVmMTIzNDU2NzgiLCJlbWFpbCI6ImFub25AaW5zZm9yZ2UuY29tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4NTU4MDJ9.-F7iyCOOvLKV_P2VSJ2RGtm1AYWrB2KTGeLM0BgBg0E'
})

export default insforge

// Database helpers
export const db = {
  // Users
  async getUsers() {
    const { data, error } = await insforge.database.from('users').select('*')
    return { data, error }
  },
  
  async createUser(user) {
    const { data, error } = await insforge.database.from('users').insert([user])
    return { data, error }
  },
  
  async updateUser(id, updates) {
    const { data, error } = await insforge.database.from('users').update(updates).eq('id', id)
    return { data, error }
  },
  
  // Leads
  async getLeads(userId) {
    const { data, error } = await insforge.database.from('leads').select('*').eq('user_id', userId)
    return { data, error }
  },
  
  async createLead(lead) {
    const { data, error } = await insforge.database.from('leads').insert([lead])
    return { data, error }
  },
  
  // Campaigns
  async getCampaigns(userId) {
    const { data, error } = await insforge.database.from('campaigns').select('*').eq('user_id', userId)
    return { data, error }
  },
  
  async createCampaign(campaign) {
    const { data, error } = await insforge.database.from('campaigns').insert([campaign])
    return { data, error }
  }
}

export default insforge
