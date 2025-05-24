import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { createCalendarEvent } from '@/lib/calendar';

export async function POST(request: Request) {
  const session = await getServerSession(authOptions);
  
  if (!session || !session.user) {
    return NextResponse.json(
      { error: 'No autorizado' },
      { status: 401 }
    );
  }

  try {
    const { appointment } = await request.json();
    
    if (!appointment) {
      return NextResponse.json(
        { error: 'Datos de la cita no proporcionados' },
        { status: 400 }
      );
    }

    // Get access token from session
    const accessToken = session.accessToken as string;
    
    // Create the calendar event
    const result = await createCalendarEvent(accessToken, {
      title: appointment.title,
      date: appointment.date,
      time: appointment.time,
      duration: appointment.duration || 30,
      timeZone: appointment.timeZone || 'America/Mexico_City',
      description: appointment.description || '',
      attendees: appointment.attendees || []
    });

    if (!result.success) {
      throw new Error(result.error || 'Error al crear el evento');
    }

    return NextResponse.json({
      success: true,
      message: 'Cita programada exitosamente',
      event: result.event
    });

  } catch (error: any) {
    console.error('Error creating calendar event:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error.message || 'Error al programar la cita' 
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({ message: 'Calendar API is running' });
}
