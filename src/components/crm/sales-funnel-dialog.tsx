'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

import { Client } from '@/types/crm';

interface SalesFunnelDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onFunnelEntrySaved: () => void;
  clients: Client[];
  entry?: any; // Entry can be a client or a funnel entry
}

export function SalesFunnelDialog({ open, onOpenChange, onFunnelEntrySaved, clients, entry }: SalesFunnelDialogProps) {
  const [formData, setFormData] = useState({
    company: '',
    stage: 'Lead',
    status: '',
    notes: '',
    estimated_value: 0,
    close_date: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (entry) {
      if (entry.type === 'client_only') {
        // Pre-fill with client data when creating a new funnel entry from a client
        setFormData({
          company: entry.company,
          stage: 'Lead',
          status: 'New Lead',
          notes: entry.client_data?.notes || '',
          estimated_value: 0,
          close_date: '',
        });
      } else {
        // Pre-fill with existing funnel entry data
        setFormData({
          company: entry.company,
          stage: entry.stage,
          status: entry.status,
          notes: entry.notes,
          estimated_value: entry.estimated_value,
          close_date: entry.close_date ? new Date(entry.close_date).toISOString().split('T')[0] : '',
        });
      }
    } else {
      // Reset form when adding a new entry from scratch
      setFormData({
        company: '',
        stage: 'Lead',
        status: '',
        notes: '',
        estimated_value: 0,
        close_date: '',
      });
    }
  }, [entry]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5001';
      let response;
      
      if (entry && entry.type !== 'client_only') {
        // Update existing funnel entry
        response = await fetch(`${API_BASE_URL}/sales_funnel/${entry.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });
      } else {
        // Create new funnel entry
        response = await fetch(`${API_BASE_URL}/sales_funnel`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });
      }

      const data = await response.json();

      if (response.ok) {
        onFunnelEntrySaved();
      } else {
        setError(data.error || 'Failed to save funnel entry');
      }
    } catch (error) {
      setError('Failed to save funnel entry');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add Funnel Entry</DialogTitle>
          <DialogDescription>
            Add a new entry to your sales funnel.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="client_id">Company *</Label>
            <Select 
              onValueChange={(value) => {
                const selectedClient = clients.find(client => client.email === value);
                setFormData({ ...formData, company: selectedClient?.company || '' });
              }}
              defaultValue={formData.company ? clients.find(c => c.company === formData.company)?.email : undefined}
              disabled={entry && entry.type === 'client_only'}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a company" />
              </SelectTrigger>
              <SelectContent>
                {clients.filter(client => client.company).map((client) => (
                  <SelectItem key={client.email} value={client.email}>
                    {client.company}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="stage">Stage *</Label>
              <Select onValueChange={(value) => setFormData({ ...formData, stage: value })} defaultValue={formData.stage}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a stage" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Lead">Lead</SelectItem>
                  <SelectItem value="Contacted">Contacted</SelectItem>
                  <SelectItem value="Proposal">Proposal</SelectItem>
                  <SelectItem value="Negotiation">Negotiation</SelectItem>
                  <SelectItem value="Won">Won</SelectItem>
                  <SelectItem value="Lost">Lost</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">Status *</Label>
              <Input
                id="status"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              placeholder="Add any relevant notes..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="estimated_value">Estimated Value</Label>
              <Input
                id="estimated_value"
                type="number"
                value={formData.estimated_value}
                onChange={(e) => setFormData({ ...formData, estimated_value: parseFloat(e.target.value) })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="close_date">Close Date</Label>
              <Input
                id="close_date"
                type="date"
                value={formData.close_date}
                onChange={(e) => setFormData({ ...formData, close_date: e.target.value })}
              />
            </div>
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded">
              {error}
            </div>
          )}

          <div className="flex justify-end space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : (entry ? 'Save' : 'Create')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}