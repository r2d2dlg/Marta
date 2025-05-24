// This component is intentionally simple.
// In a real app, you'd want to log the error to a service.
"use client";

import { Button } from "@/components/ui/button";
import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground p-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-destructive mb-4">Oops! Something went wrong.</h1>
        <p className="text-lg text-muted-foreground mb-8">
          We encountered an unexpected error. Please try again.
        </p>
        {error?.digest && (
          <p className="text-sm text-muted-foreground/70 mb-2">Error Digest: {error.digest}</p>
        )}
        <Button
          onClick={
            // Attempt to recover by trying to re-render the segment
            () => reset()
          }
          variant="destructive"
          size="lg"
        >
          Try Again
        </Button>
      </div>
    </div>
  );
}
