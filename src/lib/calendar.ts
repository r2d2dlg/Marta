import { google, calendar_v3 } from 'googleapis';
import { AppointmentDetails } from '@/types/calendar';

type CalendarEvent = calendar_v3.Schema$Event;

export async function createCalendarEvent(
  accessToken: string,
  appointment: AppointmentDetails
) {
  try {
    const event: calendar_v3.Schema$Event = {
      summary: appointment.title,
      description: appointment.description || '',
      start: {
        dateTime: `${appointment.date}T${appointment.time}:00`,
        timeZone: appointment.timeZone || 'America/Mexico_City',
      },
      end: {
        dateTime: new Date(
          new Date(`${appointment.date}T${appointment.time}:00`).getTime() + 
          appointment.duration * 60000
        ).toISOString(),
        timeZone: appointment.timeZone || 'America/Mexico_City',
      },
      attendees: appointment.attendees?.map(email => ({ email })) || [],
      reminders: {
        useDefault: true,
      },
    };

    const auth = new google.auth.OAuth2();
    auth.setCredentials({ access_token: accessToken });
    
    const calendar = google.calendar({ version: 'v3', auth });
    
    const response = await calendar.events.insert({
      calendarId: 'primary',
      requestBody: event,
      conferenceDataVersion: 1,
      sendUpdates: 'all' as const,
    });

    return {
      success: true,
      event: response.data,
      message: 'Evento creado exitosamente',
    };
  } catch (error: any) {
    console.error('Error creating calendar event:', error);
    return {
      success: false,
      error: error.message || 'Error al crear el evento',
    };
  }
}

export function validateAppointment(appointment: Partial<AppointmentDetails>) {
  if (!appointment.title) return 'Por favor ingresa un título para el evento';
  if (!appointment.date) return 'Por favor selecciona una fecha';
  if (!appointment.time) return 'Por favor selecciona una hora';
  if (!appointment.duration) return 'Por favor especifica la duración';
  return null;
}

export function formatDateForInput(date: Date): string {
  return date.toISOString().split('T')[0];
}

export function formatTimeForInput(date: Date): string {
  return date.toTimeString().slice(0, 5);
}

export function parseDateInput(dateStr: string, timeStr: string): Date {
  const [year, month, day] = dateStr.split('-').map(Number);
  const [hours, minutes] = timeStr.split(':').map(Number);
  return new Date(year, month - 1, day, hours, minutes);
}

// New function to check for calendar conflicts
export async function checkCalendarConflicts(
  accessToken: string,
  startTime: string, // ISO string e.g., 2024-05-21T10:00:00
  endTime: string,   // ISO string e.g., 2024-05-21T11:00:00
  timeZone: string
): Promise<{ hasConflict: boolean; conflictingEvents?: calendar_v3.Schema$Event[]; error?: string }> {
  try {
    const auth = new google.auth.OAuth2();
    auth.setCredentials({ access_token: accessToken });
    const calendar = google.calendar({ version: 'v3', auth });

    const response = await calendar.events.list({
      calendarId: 'primary',
      timeMin: startTime,
      timeMax: endTime,
      timeZone: timeZone,
      singleEvents: true, // Important: Expands recurring events
      orderBy: 'startTime',
      showDeleted: false,
      maxResults: 1, // We only need to know if at least one event exists
    });

    const events = response.data.items;
    if (events && events.length > 0) {
      // A conflicting event is found
      console.log('Conflict detected. Existing events:', events);
      return { hasConflict: true, conflictingEvents: events };
    }

    // No conflicting events
    return { hasConflict: false };

  } catch (error: any) {
    console.error('Error checking calendar conflicts:', error);
    return {
      hasConflict: false, // Default to no conflict on error to avoid blocking, but log it.
      error: error.message || 'Error al verificar conflictos en el calendario.',
    };
  }
}
