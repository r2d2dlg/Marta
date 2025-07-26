'use client';

import { useState, useEffect } from 'react';
import { Client, CreateClientInput, UpdateClientInput } from '@/types/crm';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Trash2, Calendar } from 'lucide-react';

interface ClientDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  client?: Client | null;
  onClientSaved: () => void;
}

export function ClientDialog({ open, onOpenChange, client, onClientSaved }: ClientDialogProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (client) {
      setFormData({
        name: client.name,
        email: client.email,
        phone: client.phone,
        company: client.company || '',
        notes: client.notes,
      });
    } else {
      setFormData({
        name: '',
        email: '',
        phone: '',
        company: '',
        notes: '',
      });
    }
    setError('');
  }, [client, open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const url = client ? `/api/crm/clients/${client.id}` : '/api/crm/clients';
      const method = client ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        onClientSaved();
      } else {
        setError(data.error || 'Failed to save client');
      }
    } catch (error) {
      setError('Failed to save client');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!client) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/crm/clients/${client.id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        onClientSaved();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to delete client');
      }
    } catch (error) {
      setError('Failed to delete client');
    } finally {
      setLoading(false);
    }
  };

  const updateLastContact = async () => {
    if (!client) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/crm/clients/${client.id}/contact`, {
        method: 'POST',
      });

      if (response.ok) {
        onClientSaved();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to update last contact');
      }
    } catch (error) {
      setError('Failed to update last contact');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {client ? 'Edit Client' : 'Add New Client'}
          </DialogTitle>
          <DialogDescription>
            {client ? 'Update client information and notes.' : 'Add a new client to your CRM system.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="company">Company</Label>
              <Input
                id="company"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email *</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number *</Label>
            <Input
              id="phone"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Add any relevant notes about this client..."
            />
          </div>

          {client && (
            <div className="text-sm text-muted-foreground space-y-1">
              <p>Created: {new Date(client.createdAt).toLocaleString()}</p>
              <p>Last Contact: {new Date(client.lastContact).toLocaleString()}</p>
              <p>Updated: {new Date(client.updatedAt).toLocaleString()}</p>
            </div>
          )}

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded">
              {error}
            </div>
          )}

          <div className="flex justify-between">
            <div className="flex space-x-2">
              {client && (
                <>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={updateLastContact}
                    disabled={loading}
                  >
                    <Calendar className="w-4 h-4 mr-2" />
                    Update Contact
                  </Button>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive" size="sm" disabled={loading}>
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete Client</AlertDialogTitle>
                        <AlertDialogDescription>
                          Are you sure you want to delete {client.name}? This action cannot be undone.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDelete}>
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </>
              )}
            </div>
            <div className="flex space-x-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Saving...' : client ? 'Update' : 'Create'}
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}