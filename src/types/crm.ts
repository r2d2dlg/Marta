export interface Client {
  id: string;
  name: string;
  email: string;
  phone: string;
  company?: string;
  notes: string;
  lastContact: string; // ISO date string
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
}

export interface CreateClientInput {
  name: string;
  email: string;
  phone: string;
  company?: string;
  notes?: string;
}

export interface UpdateClientInput {
  name?: string;
  email?: string;
  phone?: string;
  company?: string;
  notes?: string;
}