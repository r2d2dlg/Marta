// src/app/(app)/ask-marta/page.tsx

'use client';

import { useState } from 'react';
import { queryProjectDatabase } from '@/ai/flows/query-project-database'; // Corrected import path
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area'; // Assuming you might need scroll area for long responses

export default function AskMartaPage() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('Ask me anything about the project!');
  const [isLoading, setIsLoading] = useState(false);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setResponse('Searching project documentation...');

    try {
      const result = await queryProjectDatabase(query);
      setResponse(result);
    } catch (error) {
      console.error('Error querying project database:', error);
      setResponse('An error occurred while searching. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Ask Marta about the Project</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleQuery} className="flex flex-col gap-4">
            <div className="grid gap-2">
              <Label htmlFor="project-query">Your Question</Label>
              <Input
                id="project-query"
                type="text"
                placeholder="e.g., How does the file access work?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Searching...' : 'Ask Marta'}
            </Button>
          </form>

          <div className="mt-6 grid gap-2">
             <Label>Marta's Response</Label>
             <ScrollArea className="h-[200px] rounded-md border p-4 whitespace-pre-wrap">
                {response}
             </ScrollArea>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
