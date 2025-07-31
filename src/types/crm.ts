export interface AIInsights {
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  category?: 'inquiry' | 'support' | 'complaint' | 'sales' | 'general';
  sentiment?: 'positive' | 'negative' | 'neutral';
  entities?: string[];
}

export interface Client {
  id: string;
  first_name: string;
  last_name: string;
  position?: string;
  email: string;
  phone: string;
  company?: string;
  notes: string;
  lastContact: string; // ISO date string
  last_contact_source?: 'Email' | 'WhatsApp' | 'Manual';
  ai_insights?: AIInsights;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
}

export interface CreateClientInput {
  first_name: string;
  last_name: string;
  position?: string;
  email: string;
  phone: string;
  company?: string;
  notes?: string;
  last_contact_source?: 'Email' | 'WhatsApp' | 'Manual';
  ai_insights?: AIInsights;
}

export interface UpdateClientInput {
  first_name?: string;
  last_name?: string;
  position?: string;
  email?: string;
  phone?: string;
  company?: string;
  notes?: string;
  last_contact_source?: 'Email' | 'WhatsApp' | 'Manual';
  ai_insights?: AIInsights;
}