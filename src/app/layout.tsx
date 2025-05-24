import type { Metadata } from 'next';
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';
import './globals.css';
import { Toaster } from "@/components/ui/toaster";
// Import your new providers component
import { AppProviders } from './providers'; // Adjust path if you place it elsewhere

export const metadata: Metadata = {
  title: 'MartaMaria AI Assistant',
  description: 'Your personal AI assistant by MartaMaria',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${GeistSans.variable} ${GeistMono.variable}`}>
        <AppProviders> {/* Use the client component provider wrapper */}
          {children}
          <Toaster />
        </AppProviders>
      </body>
    </html>
  );
}
