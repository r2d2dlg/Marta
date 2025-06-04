"use client";

import type { Email } from '@/types';

import React, { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { toast } from '@/hooks/use-toast';
import { CheckCircle2, Edit3, RefreshCw, Send, Search, Loader2, AlertTriangle, Mail } from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatDistanceToNow } from 'date-fns';

// Import next-auth hooks and functions for client-side session management
import { useSession, signOut } from "next-auth/react";
import { redirect } from 'next/navigation'; // Import redirect for App Router

// Import the Server Actions from the actions.ts file
import { summarizeEmailAction, suggestEmailResponseAction, fetchEmailsAction, sendEmailAction } from './actions'; // Import sendEmailAction


export default function InboxPage() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [editedResponse, setEditedResponse] = useState<string>('');
  const [isAiProcessing, setIsAiProcessing] = useState(false);
  const [isLoadingEmails, setIsLoadingEmails] = useState(true);
  const [emailFetchError, setEmailFetchError] = useState<string | null>(null);
  const [isSendingEmail, setIsSendingEmail] = useState(false);


  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === 'unauthenticated') {
      redirect('/api/auth/signin');
    }
  }, [status, session]);

  useEffect(() => {
    const fetchEmails = async () => {
        if (status === 'authenticated') {
            setIsLoadingEmails(true);
            setEmailFetchError(null);
            try {
                console.log("Fetching emails via fetchEmailsAction...");
                const fetched = await fetchEmailsAction();
                setEmails(fetched);
                console.log("Emails fetched:", fetched);
            } catch (error: any) {
                console.error("Error fetching emails:", error);
                setEmailFetchError(error.message || 'Failed to fetch emails.');
                toast({
                  title: 'Error Fetching Emails',
                  description: error.message || 'Could not retrieve emails from Gmail.',
                  variant: 'destructive',
                });
            } finally {
                setIsLoadingEmails(false);
            }
        }
    };

    if (status === 'authenticated') {
        fetchEmails();
    }

  }, [status]);

  const updateEmailState = useCallback((emailId: string, updates: Partial<Email>) => {
    setEmails(prevEmails =>
      prevEmails.map(e => (e.id === emailId ? { ...e, ...updates } : e))
    );
    setSelectedEmail(prevSelected => prevSelected ? { ...prevSelected, ...updates } : null);
  }, [selectedEmail]);


  const handleSelectEmail = async (email: Email) => {
    setSelectedEmail(email);
    setEditedResponse(email.suggestedResponse); // Use existing suggested response if any

    if (status !== 'authenticated') {
        console.error("User not authenticated to process email.");
        toast({ title: 'Authentication Error', description: 'Please sign in to process emails.', variant: 'destructive' });
        return;
    }

    if (!email.summary && !email.isLoadingSummary) {
      updateEmailState(email.id, { isLoadingSummary: true });
      try {
        const summaryResult = await summarizeEmailAction(email.id);
        updateEmailState(email.id, { summary: summaryResult.summary, isLoadingSummary: false });
      } catch (error: any) {
        console.error('Error summarizing email via action:', error);
        toast({ title: 'Summary Error', description: error.message || 'Failed to summarize email.', variant: 'destructive' });
        updateEmailState(email.id, { isLoadingSummary: false, status: 'error' });
      }
    }

    if (!email.suggestedResponse && !email.isLoadingResponse && email.status !== 'error') {
      updateEmailState(email.id, { isLoadingResponse: true });
      setIsAiProcessing(true);
      try {
        const responseResult = await suggestEmailResponseAction({
          emailId: email.id,
          senderName: email.senderName,
          senderEmail: email.senderEmail,
        });
        const newSuggestedResponse = responseResult.suggestedResponse;
        updateEmailState(email.id, { suggestedResponse: newSuggestedResponse, isLoadingResponse: false });
        setEditedResponse(newSuggestedResponse);
      } catch (error: any) {
        console.error('Error generating response via action:', error);
        toast({ title: 'Response Error', description: error.message || 'Failed to generate response.', variant: 'destructive' });
        updateEmailState(email.id, { isLoadingResponse: false, status: 'error' });
      } finally {
        setIsAiProcessing(false);
      }
    }
  };

  const handleRegenerateResponse = async () => {
    if (!selectedEmail) return;

    if (status !== 'authenticated') {
        console.error("User not authenticated to regenerate response.");
        toast({ title: 'Authentication Error', description: 'Please sign in to regenerate response.', variant: 'destructive' });
        return;
    }

    updateEmailState(selectedEmail.id, { isLoadingResponse: true, status: 'pending_review' });
    setIsAiProcessing(true);
    try {
      const responseResult = await suggestEmailResponseAction({
        emailId: selectedEmail.id,
        senderName: selectedEmail.senderName,
        senderEmail: selectedEmail.senderEmail,
        userContext: "User requested regeneration. Try a different approach."
      });
      const newSuggestedResponse = responseResult.suggestedResponse;
      updateEmailState(selectedEmail.id, { suggestedResponse: newSuggestedResponse, isLoadingResponse: false });
      setEditedResponse(newSuggestedResponse);
      toast({ title: 'Success', description: 'New response generated.' });
    } catch (error: any) {
      console.error('Error regenerating response via action:', error);
      toast({ title: 'Error', description: error.message || 'Failed to regenerate response.', variant: 'destructive' });
      updateEmailState(selectedEmail.id, { isLoadingResponse: false, status: 'error' });
    } finally {
      setIsAiProcessing(false);
    }
  };

  const handleApproveAndSend = async () => {
    if (!selectedEmail || !editedResponse) {
        toast({
            title: 'Cannot Send Email',
            description: 'Please select an email and ensure there is content to send.',
            variant: 'destructive'
        });
        return;
    }

    if (status !== 'authenticated') {
        console.error("User not authenticated to send email.");
        toast({ title: 'Authentication Error', description: 'Please sign in to send emails.', variant: 'destructive' });
        return;
    }

    setIsSendingEmail(true);
    toast({ title: 'Sending Email', description: 'Attempting to send your response...', duration: 5000 });

    try {
        const sendResult = await sendEmailAction({
            to: selectedEmail.senderEmail,
            subject: `Re: ${selectedEmail.subject}`, // Prepend "Re:" for a reply
            body: editedResponse,
            originalEmailId: selectedEmail.id,
        });

        if (sendResult.success) {
            console.log('Email sent successfully, message ID:', sendResult.messageId);
            updateEmailState(selectedEmail.id, { status: 'sent' });
            toast({
                title: 'Email Sent',
                description: `Response sent to ${selectedEmail.senderName}.`,
                variant: 'default',
            });
        } else {
            console.error('Failed to send email:', sendResult.error);
             toast({
                title: 'Failed to Send Email',
                description: sendResult.error || 'An error occurred while sending the email.',
                variant: 'destructive',
            });
             updateEmailState(selectedEmail.id, { status: 'error' });
        }

    } catch (error: any) {
        console.error('Error calling sendEmailAction:', error);
         toast({
            title: 'Failed to Send Email',
            description: error.message || 'An unexpected error occurred.',
            variant: 'destructive',
        });
         updateEmailState(selectedEmail.id, { status: 'error' });
    } finally {
        setIsSendingEmail(false);
    }
  };

  const handleSaveDraft = () => {
    if (!selectedEmail) return;
    updateEmailState(selectedEmail.id, { status: 'draft', suggestedResponse: editedResponse });
    toast({ title: 'Draft Saved', description: `Draft for ${selectedEmail.senderName} saved.` });
  };

  const getStatusBadgeVariant = (status: Email['status']) => {
    switch (status) {
      case 'approved': return 'default';
      case 'pending_review': return 'secondary';
      case 'draft': return 'outline';
      case 'sent': return 'default';
      case 'error': return 'destructive';
      default: return 'secondary';
    }
  };

  if (status === 'loading' || isLoadingEmails) {
    return (
        <div className="flex h-full items-center justify-center">
           <Loader2 className="h-8 w-8 animate-spin text-primary" />
           <span className="ml-2 text-muted-foreground">Loading Inbox...</span>
        </div>
    );
  }

  if (status === 'authenticated' && emailFetchError) {
    return (
      <div className="flex h-full items-center justify-center">
        <AlertTriangle className="h-8 w-8 text-destructive" />
        <span className="ml-2 text-destructive">Error: {emailFetchError}</span>
      </div>
    );
  }


  return (
    status === 'authenticated' && !isLoadingEmails && (
      <div className="flex h-[calc(100vh-theme(spacing.16)-theme(spacing.12))] gap-6">
        <Card className="w-1/3 flex flex-col shadow-lg">
          <CardHeader>
            <CardTitle>Client Emails</CardTitle>
            <CardDescription>{emails.filter(e => e.status === 'pending_review').length} emails pending review.</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow p-0">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-3">
                 {emails.length === 0 && !isLoadingEmails && (
                     <div className="flex flex-col items-center justify-center text-center text-muted-foreground py-8">
                         <Mail className="h-12 w-12 mb-4" />
                         <p className="text-lg font-semibold">No Emails Found</p>
                         <p className="text-sm">Check your Gmail inbox or try refreshing.</p>
                     </div>
                 )}
                {emails.map((email) => (
                  <button
                    key={email.id}
                    onClick={() => handleSelectEmail(email)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors hover:bg-muted/50 ${
                      selectedEmail?.id === email.id ? 'bg-muted ring-2 ring-primary' : 'bg-card'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                         <Avatar className="h-8 w-8">
                           <AvatarImage src={`https://picsum.photos/seed/${email.senderEmail}/40/40`} data-ai-hint="person avatar" />
                           <AvatarFallback>{email.senderName.substring(0, 2).toUpperCase()}</AvatarFallback>
                         </Avatar>
                        <span className="font-semibold text-sm">{email.senderName}</span>
                      </div>
                      <Badge variant={getStatusBadgeVariant(email.status)} className="text-xs capitalize">{email.status.replace('_', ' ')}</Badge>
                    </div>
                    <p className="text-sm font-medium truncate">{email.subject}</p>
                    <p className="text-xs text-muted-foreground truncate">{email.summary || email.originalContent}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(email.receivedAt, { addSuffix: true })}
                    </p>
                  </button>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        <Card className="w-2/3 flex flex-col shadow-lg">
          {selectedEmail ? (
            <>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-2xl">{selectedEmail.subject}</CardTitle>
                    <CardDescription>
                      From: {selectedEmail.senderName} ({selectedEmail.senderEmail})
                    </CardDescription>
                  </div>
                  <Badge variant={getStatusBadgeVariant(selectedEmail.status)} className="capitalize text-sm">
                    {selectedEmail.status.replace('_', ' ')}
                  </Badge>
                </div>
              </CardHeader>
              <Separator />
              <CardContent className="flex-grow flex flex-col gap-4 pt-6 overflow-y-auto">
                <div>
                  <h3 className="font-semibold mb-2 text-foreground">Original Email Content:</h3>
                  {selectedEmail.isLoadingSummary || selectedEmail.isLoadingResponse ? (
                     <div className="flex items-center space-x-2 text-muted-foreground h-32 justify-center border rounded-md p-3 bg-muted/20">
                        <Loader2 className="h-4 w-4 animate-spin" /> <span>Loading email content...</span>
                     </div>
                  ) : (
                    <ScrollArea className="h-32 rounded-md border p-3 bg-muted/20">
                      <p className="text-sm text-muted-foreground">
                        {selectedEmail.originalContent || 'Could not load email content.'}
                      </p>
                    </ScrollArea>
                  )}
                </div>

                <div>
                  <h3 className="font-semibold mb-2 text-foreground">Suggested Response:</h3>
                  {selectedEmail.isLoadingResponse || (isAiProcessing && selectedEmail.status === 'pending_review' && !selectedEmail.suggestedResponse) ? (
                    <div className="flex items-center space-x-2 text-muted-foreground h-48 justify-center">
                      <Loader2 className="h-6 w-6 animate-spin text-primary" /> <span>MartaMaria is typing...</span>
                    </div>
                  ) : selectedEmail.status === 'error' && !selectedEmail.isLoadingResponse ? (
                     <div className="flex flex-col items-center justify-center text-destructive h-48 border border-destructive/50 rounded-md p-4">
                       <AlertTriangle className="h-8 w-8 mb-2" />
                       <p className="font-semibold">Error Generating Response</p>
                       <p className="text-sm text-center">MartaMaria encountered an issue. Please try again.</p>
                     </div>
                  ) : (
                    <Textarea
                      value={editedResponse}
                      onChange={(e) => setEditedResponse(e.target.value)}
                      placeholder="MartaMaria's suggested response will appear here..."
                      className="min-h-[200px] text-base focus:ring-accent"
                      disabled={isAiProcessing || selectedEmail.isLoadingResponse || isSendingEmail}
                    />
                  )}
                </div>
              </CardContent>
              <Separator />
              <CardFooter className="py-4 flex justify-end gap-2">
                <Button variant="outline" onClick={handleSaveDraft} disabled={isAiProcessing || selectedEmail.isLoadingResponse || selectedEmail.status === 'approved' || isSendingEmail}> 
                  <Edit3 className="mr-2 h-4 w-4" /> Save Draft
                </Button>
                <Button variant="secondary" onClick={handleRegenerateResponse} disabled={isAiProcessing || selectedEmail.isLoadingResponse || isSendingEmail}> 
                  {isAiProcessing && selectedEmail.isLoadingResponse ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                  Regenerate
                </Button>
                <Button
                   onClick={handleApproveAndSend}
                   className="bg-primary hover:bg-primary/90"
                   disabled={isAiProcessing || selectedEmail.isLoadingResponse || !editedResponse || selectedEmail.status === 'approved' || isSendingEmail}
                >
                   {isSendingEmail ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <CheckCircle2 className="mr-2 h-4 w-4" />}
                  {isSendingEmail ? 'Sending...' : 'Approve & Send'}
                </Button>
              </CardFooter>
            </>
          ) : (
            <div className="flex-grow flex flex-col items-center justify-center text-center p-6">
              <Mail className="h-24 w-24 text-muted-foreground/50 mb-6" />
              <h2 className="text-2xl font-semibold text-muted-foreground">Select an Email</h2>
              <p className="text-sm text-muted-foreground">Choose an email from the list to view its details and AI-suggested response.</p>
            </div>
          )}
        </Card>
      </div>
    )
  );
}
