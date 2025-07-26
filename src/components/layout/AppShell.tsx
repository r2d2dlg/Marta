"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Mail, FileText, Settings, BotMessageSquare, MessageSquare, UserCircle, Users } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  SidebarProvider,
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarTrigger,
  SidebarInset,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroupLabel,
  SidebarGroup,
} from '@/components/ui/sidebar';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// Import next-auth hooks and functions
import { useSession, signIn, signOut } from "next-auth/react";

const navItems = [
  { href: '/inbox', label: 'Inbox', icon: Mail },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/crm', label: 'CRM', icon: Users },
  { href: '/files', label: 'Files', icon: FileText },
  { href: '/ask-marta', label: 'Ask Marta', icon: BotMessageSquare },
  // { href: '/settings', label: 'Settings', icon: Settings }, // Future placeholder
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  // Use the useSession hook
  const { data: session, status } = useSession();

  return (
    <SidebarProvider>
      <Sidebar variant="sidebar" collapsible="icon" side="left">
        <SidebarHeader className="p-4">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10 bg-primary text-primary-foreground">
              <AvatarFallback>MM</AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-xl font-semibold text-sidebar-foreground">MartaMaria</h1>
              <p className="text-xs text-sidebar-foreground/70">AI Assistant</p>
            </div>
          </div>
        </SidebarHeader>
        <SidebarContent>
          <SidebarMenu>
            {navItems.map((item) => (
              <SidebarMenuItem key={item.href}>
                <Link href={item.href} legacyBehavior passHref>
                  <SidebarMenuButton
                    isActive={pathname.startsWith(item.href)}
                    tooltip={item.label}
                    className="justify-start"
                  >
                    <item.icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </SidebarMenuButton>
                </Link>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarContent>
        {/* <SidebarFooter className="p-2">
          <Button variant="ghost" className="w-full justify-start">
            <Settings className="mr-2 h-4 w-4" /> Settings
          </Button>
        </SidebarFooter> */}
      </Sidebar>
      <SidebarInset className="flex flex-col">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b bg-background/80 px-4 backdrop-blur-sm md:px-6">
          <div className="flex items-center gap-2">
             <SidebarTrigger className="md:hidden" /> {/* Hidden on desktop, visible on mobile to toggle sheet */}
             <h2 className="text-lg font-semibold">
                {navItems.find(item => pathname.startsWith(item.href))?.label || 'Dashboard'}
             </h2>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              {/* Show user avatar if authenticated, otherwise a generic icon or text */}
              <Button variant="ghost" size="icon" className="rounded-full">
                {status === 'authenticated' && session?.user?.image ? (
                   <Avatar className="h-8 w-8">
                     <AvatarImage src={session.user.image} alt={`${session.user.name || 'User'} Avatar`} />
                     <AvatarFallback>{session.user.email?.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
                   </Avatar>
                ) : (
                   <UserCircle className="h-8 w-8" /> // Generic icon when not authenticated
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {status === 'authenticated' ? (
                <>
                  <DropdownMenuLabel>
                     {session.user?.name || session.user?.email || 'My Account'}
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {/* Optional: Add Profile and Settings links */}
                  <DropdownMenuItem>Profile</DropdownMenuItem>
                  <DropdownMenuItem>Settings</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  {/* Sign out button */}
                  <DropdownMenuItem onClick={() => { console.log('Logout button clicked'); signOut(); }}>
                     Logout
                  </DropdownMenuItem>
                </>
              ) : (
                // Show Sign in button when not authenticated
                <DropdownMenuItem onClick={() => { console.log('Logout button clicked - signOut() removed for test'); }}>
                  Sign In
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
