import { NextRequest, NextResponse } from 'next/server';
import { sendEmailAction } from '@/app/(app)/inbox/actions';

export async function POST(request: NextRequest) {
  try {
    const { to, subject, body } = await request.json();
    if (!to || !subject || !body) {
      return NextResponse.json({ success: false, error: 'Faltan campos requeridos (to, subject, body).' }, { status: 400 });
    }
    const result = await sendEmailAction({ to, subject, body });
    if (result.success) {
      return NextResponse.json({ success: true, messageId: result.messageId });
    } else {
      return NextResponse.json({ success: false, error: result.error || 'Error desconocido al enviar el correo.' }, { status: 500 });
    }
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message || 'Error inesperado.' }, { status: 500 });
  }
} 