import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { redirect } from 'next/navigation';
import { ChatInterface } from '@/components/chat-interface';

export default async function ChatPage() {
  const session = await getServerSession(authOptions);
  
  if (!session) {
    redirect('/api/auth/signin');
  }

  return (
    <div className="container mx-auto p-4 h-[calc(100vh-64px)]">
      <h1 className="text-2xl font-bold mb-6">Asistente de Correo</h1>
      <div className="h-full">
        <ChatInterface />
      </div>
    </div>
  );
}
