"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { FileText } from "lucide-react";

// Import next-auth hooks and functions
import { useSession } from "next-auth/react";
import { redirect } from 'next/navigation'; // Import redirect for App Router
import { useEffect } from "react";


export default function FilesPage() {
  // Use the useSession hook
  const { data: session, status } = useSession();

  // Authentication check effect
  useEffect(() => {
    if (status === 'unauthenticated') {
      // Redirect to the sign-in page if not authenticated
      redirect('/api/auth/signin');
    }
    // Optional: Check for specific email if needed
    // if (status === 'authenticated' && session?.user?.email !== 'mmendez@datanalisis.io') {
    //   // Redirect or show an error if the wrong user is logged in
    //   signOut({ callbackUrl: '/' }); // Sign out and redirect to home
    // }
  }, [status, session]); // Rerun effect when status or session changes

  // Render nothing or a loading spinner while the session is loading
  if (status === 'loading') {
    return <div>Loading...</div>; // Or a more sophisticated loading component
  }

  // Only render the page content if authenticated
  return (
     status === 'authenticated' && (
      <div className="container mx-auto py-8">
        <Card className="shadow-lg">
          <CardHeader>
            <div className="flex items-center gap-3 mb-2">
              <FileText className="h-8 w-8 text-primary" />
              <CardTitle className="text-3xl">File Access</CardTitle>
            </div>
            <CardDescription>Manage and access your files with MartaMaria.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-muted-foreground/30 rounded-lg bg-muted/10">
              <FileText className="h-16 w-16 text-muted-foreground/50 mb-4" />
              <p className="text-lg text-muted-foreground">File management features are under development.</p>
              <p className="text-sm text-muted-foreground/80">Soon you'll be able to interact with your documents here.</p>
            </div>
          </CardContent>
        </Card>
      </div>
     )
  );
}
