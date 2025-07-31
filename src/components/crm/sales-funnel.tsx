'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { SalesFunnelDialog } from './sales-funnel-dialog';

export function SalesFunnel() {
  const [funnelData, setFunnelData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const [clients, setClients] = useState<{ id: number; company: string }[]>([]);

  const fetchClients = async () => {
    try {
      const response = await fetch('/api/crm/clients');
      const data = await response.json();
      if (response.ok) {
        setClients(data.clients);
      } else {
        console.error('Failed to fetch clients:', data.error);
      }
    } catch (error) {
      console.error('Error fetching clients:', error);
    }
  };

  const fetchFunnelData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/sales_funnel');
      const data = await response.json();
      if (response.ok) {
        setFunnelData(data);
      } else {
        console.error('Failed to fetch sales funnel data:', data.error);
      }
    } catch (error) {
      console.error('Error fetching sales funnel data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFunnelEntrySaved = () => {
    fetchFunnelData();
    setIsDialogOpen(false);
  };

  useEffect(() => {
    fetchFunnelData();
    fetchClients();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Sales Funnel</h2>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Funnel Entry
        </Button>
      </div>

      {/* You can add your sales funnel visualization here. */}
      {/* For now, I'll just display the raw data. */}
      <pre className="bg-slate-100 p-4 rounded-md">
        {JSON.stringify(funnelData, null, 2)}
      </pre>

      <SalesFunnelDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        onFunnelEntrySaved={handleFunnelEntrySaved}
        clients={clients}
      />
    </div>
  );
}
