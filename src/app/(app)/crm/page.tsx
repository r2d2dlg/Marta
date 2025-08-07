'use client';

import { useState, useEffect } from 'react';
import { Client } from '@/types/crm';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Search, Plus, Phone, Mail, Building, Calendar, User } from 'lucide-react';
import { ClientDialog } from '@/components/crm/client-dialog';
import { SalesFunnel } from '@/components/crm/sales-funnel';
import { CRMService } from '@/lib/crm';

export default function CRMPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('clients');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);

  const fetchClients = async (search?: string) => {
    try {
      const data = search ? await CRMService.searchClients(search) : await CRMService.getAllClients();
      setClients(data);
    } catch (error) {
      console.error('Error fetching clients:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.length > 0) {
      fetchClients(query);
    } else {
      fetchClients();
    }
  };

  const handleClientSaved = async (client: Client | null) => {
    if (client) {
      if (selectedClient) {
        // Update existing client
        const updatedClient = await CRMService.updateClient(client.id, client);
        setClients(clients.map(c => c.id === updatedClient.id ? updatedClient : c));
      } else {
        // Add new client
        const newClient = await CRMService.createClient(client);
        setClients([newClient, ...clients]);
      }
    } else {
      // Client was deleted
      if (selectedClient) {
        await CRMService.deleteClient(selectedClient.id);
        setClients(clients.filter(c => c.id !== selectedClient.id));
      }
    }
    setIsDialogOpen(false);
    setSelectedClient(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">CRM - Cliente Management</h1>
          <p className="text-muted-foreground">
            Manage your client relationships and track interactions
          </p>
        </div>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Client
        </Button>
      </div>

      <div className="flex items-center space-x-2">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search clients..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-8"
            />
          </div>
          <Badge variant="secondary">
            {clients.length} client{clients.length !== 1 ? 's' : ''}
          </Badge>
        </div>

        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            <a key="clients-tab" href="#" onClick={() => setActiveTab('clients')} className={`${activeTab === 'clients' ? 'border-sky-500 text-sky-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}> Clients </a>
            <a key="sales-funnel-tab" href="#" onClick={() => setActiveTab('sales_funnel')} className={`${activeTab === 'sales_funnel' ? 'border-sky-500 text-sky-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}> Sales Funnel </a>
          </nav>
        </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading clients...</div>
        </div>
      ) : activeTab === 'clients' && clients.length === 0 ? (
        <Card key="no-clients-card">
          <CardContent className="flex flex-col items-center justify-center py-16">
            <User className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No clients found</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery ? 'No clients match your search criteria.' : 'Get started by adding your first client.'}
            </p>
            {!searchQuery && (
              <Button onClick={() => setIsDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Add First Client
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div>
          {activeTab === 'clients' && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {clients.map((client, index) => (
                <Card 
                  key={client.id || `client-${client.email}-${index}`} 
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => {
                    setSelectedClient(client);
                    setIsDialogOpen(true);
                  }}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">{client.first_name} {client.last_name}</CardTitle>
                    {client.company && (
                      <CardDescription className="flex items-center">
                        <Building className="w-3 h-3 mr-1" />
                        {client.company}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Mail className="w-3 h-3 mr-2" />
                      {client.email}
                    </div>
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Phone className="w-3 h-3 mr-2" />
                      {client.phone}
                    </div>
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Calendar className="w-3 h-3 mr-2" />
                      Last contact: {formatDate(client.lastContact)}
                    </div>
                    {client.notes && (
                      <p className="text-sm text-muted-foreground line-clamp-2 mt-2">
                        {client.notes}
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {activeTab === 'sales_funnel' && <SalesFunnel clients={clients} />}
        </div>
      )}

      <ClientDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        client={selectedClient}
        onClientSaved={handleClientSaved}
      />
    </div>
  );
}