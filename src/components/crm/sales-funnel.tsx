'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { SalesFunnelDialog } from './sales-funnel-dialog';
import { CRMService } from '@/lib/crm';
import { Client } from '@/types/crm';

const FUNNEL_STAGES = ['Lead', 'Contacted', 'Proposal', 'Negotiation', 'Won', 'Lost'];

interface SalesFunnelProps {
  clients: Client[];
}

export function SalesFunnel({ clients }: SalesFunnelProps) {
  const [funnelData, setFunnelData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('Lead');
  const [selectedEntry, setSelectedEntry] = useState<any | null>(null);

  const fetchFunnelData = async () => {
    setLoading(true);
    try {
      const data = await CRMService.getAllSalesFunnelEntries();
      setFunnelData(data);
    } catch (error) {
      console.error('Error fetching sales funnel data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFunnelEntrySaved = () => {
    fetchFunnelData();
    setIsDialogOpen(false);
    setSelectedEntry(null);
  };

  const handleEditEntry = (entry: any) => {
    setSelectedEntry(entry);
    setIsDialogOpen(true);
  };

  // Organize data by funnel stage
  const organizeDataByStage = () => {
    const organized: Record<string, any[]> = {};
    
    // Initialize all stages
    FUNNEL_STAGES.forEach(stage => {
      organized[stage] = [];
    });

    // Create a map of companies with funnel entries
    const companiesWithFunnelEntries = new Set(funnelData.map((entry: any) => entry.company));

    // Add funnel entries to their respective stages
    funnelData.forEach((entry: any) => {
      const stage = entry.stage || 'Lead';
      if (organized[stage]) {
        organized[stage].push({
          ...entry,
          type: 'funnel_entry'
        });
      }
    });

    // Add companies without funnel entries to Lead stage
    clients.forEach((client: any) => {
      if (client.company && !companiesWithFunnelEntries.has(client.company)) {
        organized['Lead'].push({
          id: client.id, // Use client ID as the key
          company: client.company,
          stage: 'Lead',
          status: 'New Lead',
          type: 'client_only',
          client_data: client
        });
      }
    });

    return organized;
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'Won': return 'bg-green-100 text-green-800 border-green-200';
      case 'Lost': return 'bg-red-100 text-red-800 border-red-200';
      case 'Proposal': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'Negotiation': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'Contacted': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTabColor = (stage: string) => {
    switch (stage) {
      case 'Won': return 'border-green-500 text-green-600';
      case 'Lost': return 'border-red-500 text-red-600';
      case 'Proposal': return 'border-blue-500 text-blue-600';
      case 'Negotiation': return 'border-yellow-500 text-yellow-600';
      case 'Contacted': return 'border-purple-500 text-purple-600';
      default: return 'border-gray-500 text-gray-600';
    }
  };

  useEffect(() => {
    fetchFunnelData();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  const organizedData = organizeDataByStage();
  const currentStageData = organizedData[activeTab] || [];

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">Sales Funnel</h2>
        <Button onClick={() => setIsDialogOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Funnel Entry
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6 overflow-x-auto">
        {FUNNEL_STAGES.map((stage) => (
          <button
            key={stage}
            onClick={() => setActiveTab(stage)}
            className={`px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
              activeTab === stage
                ? `${getTabColor(stage)} border-b-2`
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {stage}
            <span className="ml-2 bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
              {organizedData[stage]?.length || 0}
            </span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {currentStageData.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No companies in the {activeTab} stage yet.</p>
            {activeTab === 'Lead' && (
              <p>Companies without funnel entries will appear here automatically.</p>
            )}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {currentStageData.map((entry: any, index: number) => (
              <div key={entry.id || `${entry.type}-${entry.company}-${index}`} className={`bg-white border rounded-lg p-4 shadow-sm ${getStageColor(entry.stage)}`}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-lg">{entry.company}</h3>
                  <Button variant="ghost" size="sm" onClick={() => handleEditEntry(entry)}>
                    Edit
                  </Button>
                  <span className={`px-2 py-1 rounded-full text-xs ${getStageColor(entry.stage)}`}>
                    {entry.stage}
                  </span>
                </div>
                <div className="space-y-1 text-sm text-gray-600">
                  <p><strong>Status:</strong> {entry.status}</p>
                  {entry.estimated_value && (
                    <p><strong>Value:</strong> ${entry.estimated_value.toLocaleString()}</p>
                  )}
                  {entry.close_date && (
                    <p><strong>Close Date:</strong> {new Date(entry.close_date).toLocaleDateString()}</p>
                  )}
                  {entry.notes && (
                    <p><strong>Notes:</strong> {entry.notes}</p>
                  )}
                  {entry.type === 'client_only' && (
                    <p className="text-xs italic text-gray-500">Contact: {entry.client_data?.first_name} {entry.client_data?.last_name}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <SalesFunnelDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        onFunnelEntrySaved={handleFunnelEntrySaved}
        clients={clients}
        entry={selectedEntry}
      />
    </div>
  );
}