import fs from 'fs'; import path from 'path';

"use server";

// Import server-side functions and authOptions
import { getServerSession } from "next-auth";
// Import authOptions from the new location
import { authOptions } from "@/auth";
// Import the server-side Genkit flow functions
import { summarizeEmails, SummarizeEmailsInput } from '@/ai/flows/summarize-emails';
import { suggestEmailResponse, SuggestEmailResponseInput } from '@/ai/flows/suggest-email-responses';
import { google } from 'googleapis';
import { addDays, format, parseISO, isToday, isTomorrow, formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { AppointmentDetails, AppointmentState, AppointmentStep } from '@/types/calendar';
import { createCalendarEvent, validateAppointment, checkCalendarConflicts } from '@/lib/calendar';

// Import the Email type from your types file
import type { Email } from '@/types';

// Helper function to create the raw email content in MIME format
function createMimeMessage(to: string, from: string, subject: string, body: string, inReplyToMessageId?: string, referencesMessageId?: string): string {
  const boundary = '------------Boundaryodarai';
  // Encode subject as UTF-8 base64 per MIME standards
  const encodedSubject = `=?UTF-8?B?${Buffer.from(subject, 'utf-8').toString('base64')}?=`;
  const lines = [
    `From: ${from}`,
    `To: ${to}`,
    `Subject: ${encodedSubject}`,
    `MIME-Version: 1.0`,
    `Content-Type: multipart/alternative; boundary="${boundary}"`
  ];

  if (inReplyToMessageId) {
    lines.push(`In-Reply-To: <${inReplyToMessageId}>`);
  }
  if (referencesMessageId) {
    lines.push(`References: <${referencesMessageId}>`);
  }

  lines.push(''); // Blank line to separate headers from body

  // Plain text part
  lines.push(`--${boundary}`);
  lines.push(`Content-Type: text/plain; charset="UTF-8"`);
  lines.push(`Content-Transfer-Encoding: base64`);
  lines.push('');
  lines.push(Buffer.from(body).toString('base64'));

  lines.push(`--${boundary}--`);

  return lines.join('\r\n'); // Corrected: Standard CRLF for email line endings
}

// Define Server Action to send an email via Gmail API
export const sendEmailAction = async (emailDetails: { to: string; subject: string; body: string; originalEmailId?: string }): Promise<{ success: boolean; messageId?: string; error?: string }> => {
    const session = await getServerSession(authOptions);

    if (!session || !session.user || !session.user.email) {
        console.error("Unauthorized access to sendEmailAction");
        return { success: false, error: "Unauthorized: User not authenticated." };
    }

    const accessToken = (session as any).accessToken as string;
    const fromEmail = session.user.email; // The 'From' address should be the authenticated user's email

    if (!accessToken) {
        console.error("Access token not found in session for sendEmailAction");
        return { success: false, error: "Authentication error: Access token not found." };
    }

     if (!fromEmail) {
        console.error("Authenticated user email not found in session for sendEmailAction");
        return { success: false, error: "Authentication error: User email not found." };
    }


    console.log(`Attempting to send email from ${fromEmail} to ${emailDetails.to}...`);

    try {
        const oauth2Client = new google.auth.OAuth2();
        oauth2Client.setCredentials({ access_token: accessToken });

        const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

        // Create the raw email content in MIME format
        const rawEmail = createMimeMessage(
            emailDetails.to,
            fromEmail,
            emailDetails.subject,
            emailDetails.body,
            emailDetails.originalEmailId, // Pass original ID for threading
            emailDetails.originalEmailId  // Pass original ID for threading
        );

        // Send the email
        const sendResponse = await gmail.users.messages.send({
            userId: 'me',
            requestBody: {
                raw: Buffer.from(rawEmail).toString('base64url'), // Encode the whole message in base64url
            },
        });

        console.log("Email sent successfully:", sendResponse.data);

        return { success: true, messageId: sendResponse.data.id ?? undefined };

    } catch (error: any) {
        console.error("Error sending email via Gmail API:", error);
        // Provide a more detailed error message from the Google API if possible
        const errorMessage = error.response?.data?.error?.message || error.message || 'Failed to send email.';
        return { success: false, error: errorMessage };
    }
};


// Define Server Action to fetch emails from Gmail
export const fetchEmailsAction = async (): Promise<Email[]> => {
  const session = await getServerSession(authOptions);
  if (!session || !session.user) {
    console.error("Unauthorized access to fetchEmailsAction");
    throw new Error("Unauthorized: User not authenticated to fetch emails.");
  }
  const accessToken = (session as any).accessToken as string;
  if (!accessToken) {
      console.error("Access token not found in session for fetchEmailsAction");
      throw new Error("Authentication error: Access token not found for fetching emails.");
  }
  console.log("Attempting to fetch emails from Gmail API...");
  try {
    const oauth2Client = new google.auth.OAuth2();
    oauth2Client.setCredentials({ access_token: accessToken });
    const gmail = google.gmail({ version: 'v1', auth: oauth2Client });
    const listResponse = await gmail.users.messages.list({
      userId: 'me',
      labelIds: ['INBOX'],
      maxResults: 20,
    });
    const messages = listResponse.data.messages;
    const fetchedEmails: Email[] = [];
    if (messages && messages.length > 0) {
      console.log(`Found ${messages.length} messages. Fetching details...`);
      for (const message of messages) {
        if (message.id) {
            try {
                const msgDetails = await gmail.users.messages.get({
                    userId: 'me',
                    id: message.id,
                    format: 'metadata',
                    metadataHeaders: ['Subject', 'From', 'Date'],
                });
                const payload = msgDetails.data.payload;
                const headers = payload?.headers;
                const subject = headers?.find(h => h.name === 'Subject')?.value || 'No Subject';
                const fromHeader = headers?.find(h => h.name === 'From')?.value || 'Unknown Sender <unknown@example.com>';
                const dateHeader = headers?.find(h => h.name === 'Date')?.value;
                const senderMatch = fromHeader.match(/(.*)<(.*)>/);
                const senderName = senderMatch ? senderMatch[1].trim() : fromHeader;
                const senderEmail = senderMatch ? senderMatch[2].trim() : 'unknown@example.com';
                const snippet = msgDetails.data.snippet || 'No snippet available.';
                const receivedAt = dateHeader ? new Date(dateHeader) : new Date();
                fetchedEmails.push({
                    id: message.id,
                    senderName,
                    senderEmail,
                    subject: subject,
                    originalContent: snippet, // Use snippet for list view for now
                    summary: snippet, // Use snippet as initial summary
                    suggestedResponse: '',
                    status: 'pending_review',
                    receivedAt: receivedAt,
                    isLoadingSummary: false,
                    isLoadingResponse: false,
                });
            } catch (detailError) {
                 console.error(`Error fetching details for message ID ${message.id}:`, detailError);
            }
        }
      }
      console.log(`Successfully fetched details for ${fetchedEmails.length} emails.`);
    } else {
      console.log('No messages found in the inbox.');
    }
    return fetchedEmails;
  } catch (error) {
    console.error("Error fetching emails from Gmail API:", error);
    throw new Error("Failed to fetch emails from Gmail.");
  }
};


// Define Server Action for email summarization
export const summarizeEmailAction = async (emailId: string) => {
  const session = await getServerSession(authOptions);
  if (!session || !session.user) {
    console.error("Unauthorized access to summarizeEmailAction");
    throw new Error("Unauthorized: User not authenticated.");
  }
  
  try {
    // Use the local implementation instead of Vertex AI
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:9002';
    const response = await fetch(`${baseUrl}/api/ask-marta`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        query: `Summarize the email with ID: ${emailId}`
      }),
      cache: 'no-store'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get summary from API');
    }
    
    const data = await response.json();
    return { 
      summary: data.response,
      keyPoints: data.response.split('. ').slice(0, 3).map((point: string) => point.trim() + '.')
    };
  } catch (error) {
    console.error("Error in summarizeEmailAction:", error);
    return { 
      summary: "I'm sorry, I couldn't generate a summary at this time. Please try again later.",
      keyPoints: []
    };
  }
};

// Define Server Action for suggesting email responses
// Define Server Action to handle natural language queries about emails and appointments
export const handleAssistantQuery = async (query: string): Promise<{ response: string; data?: any }> => {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    console.error("Unauthorized access to handleAssistantQuery");
    return { response: "Lo siento, necesitas iniciar sesión para realizar esta acción." };
  }

  try {
    // Preprocess query to remove greetings and courtesy phrases
    let cleanQuery = query
      .replace(/hola marta[.,]?/i, '')
      .replace(/hola[.,]?/i, '')
      .replace(/por favor[.,]?/i, '')
      .replace(/favor[.,]?/i, '')
      .trim();

    // Mejorada: detectar 'enviale un e-mail a NOMBRE. Su e-mail es CORREO ...' o variantes
    // 1. Buscar nombre y correo aunque estén en frases separadas
    let name = '';
    let to = '';
    // Caso: "enviale un e-mail a NOMBRE. Su e-mail es CORREO"
    const nameEmailMatch = cleanQuery.match(/env[ií]ale?\s+un\s+(?:correo|e[- ]?mail|email)\s+a\s+([\wáéíóúüñÁÉÍÓÚÜÑ .,'-]+)[.\s,;:]+su\s+e[- ]?mail\s+es\s+([\w.-]+@[\w.-]+)/i);
    if (nameEmailMatch) {
      name = nameEmailMatch[1].trim();
      to = nameEmailMatch[2].trim();
    } else {
      // Caso: "enviale un e-mail a CORREO ..." (sin nombre)
      const emailOnlyMatch = cleanQuery.match(/env[ií]ale?\s+un\s+(?:correo|e[- ]?mail|email)\s+a\s+([\w.-]+@[\w.-]+)/i);
      if (emailOnlyMatch) {
        to = emailOnlyMatch[1].trim();
      } else {
        // Caso: "su e-mail es CORREO" (buscar correo en cualquier parte)
        const anyEmailMatch = cleanQuery.match(/([\w.-]+@[\w.-]+)/i);
        if (anyEmailMatch) {
          to = anyEmailMatch[1].trim();
        }
      }
      // Buscar nombre si está presente
      const nameMatch = cleanQuery.match(/env[ií]ale?\s+un\s+(?:correo|e[- ]?mail|email)\s+a\s+([\wáéíóúüñÁÉÍÓÚÜÑ .,'-]+)/i);
      if (nameMatch) {
        name = nameMatch[1].trim();
      }
    }
    // Si se detectó un correo destinatario, generar el borrador
    if (to) {
      // Extrae solo el e-mail válido
      const emailMatch = to.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
      let clientEmail: string | undefined = undefined;
      if (emailMatch) {
        clientEmail = emailMatch[0];
        to = clientEmail; // ensure 'to' is the cleaned email for display
      } else {
        return {
          response: 'No se detectó un e-mail válido para el destinatario. Por favor, revisa la dirección e inténtalo de nuevo.'
        };
      }
      const subject = 'Presentación de los servicios de datanalisis.io';
      let saludo = 'Estimado/a';
      if (name) {
        // Usar solo el primer nombre y primer apellido si hay varios
        const nombreCorto = name.split(' ').slice(0, 2).join(' ');
        saludo = `Estimado/a ${nombreCorto}`;
      }
      let body = `${saludo},\n\nMi nombre es Marta y soy la asistente de IA de Datanalisis.io.\n\nDatanalisis.io se especializa en proveer soluciones avanzadas de Inteligencia de Negocios (BI) e Inteligencia Artificial (AI) para ayudar a las organizaciones a optimizar sus operaciones, automatizar procesos y tomar decisiones basadas en datos. Ofrecemos desarrollo de dashboards, automatización con AI (para facturación, órdenes de compra/servicio, atención al cliente), y BI por departamento (RRHH, Cobros, Contabilidad, Marketing).\n\nNuestro objetivo es que los líderes empresariales logren claridad operativa y control total, transformando datos en valor y ventajas competitivas. Ayudamos a integrar fuentes de datos, identificar eficiencias y mejorar procesos de forma medible y escalable.\n\nSi desea conocer más sobre cómo Datanalisis.io puede apoyar a su empresa, estaré encantada de coordinar una reunión o responder cualquier consulta específica que tenga sobre nuestras soluciones de BI y AI.\n\nQuedo atenta a su respuesta.\n\nSaludos cordiales,\nMarta Mendez - AI\ndatanalisis.io`;
      // Si hay un motivo adicional, agrégalo
      const purposeMatch = cleanQuery.match(/pres[ée]ntale?\s+nuestros?\s+servicios?([\s\S]*)/i);
      if (purposeMatch && purposeMatch[1].trim()) {
        body += `\n\nMotivo adicional: ${purposeMatch[1].trim()}`;
      }
      return {
        response: `He preparado el siguiente borrador de correo para ${to}:\n\nAsunto: ${subject}\n\n${body}\n\n¿Deseas enviarlo, editarlo o descartarlo?`,
        data: {
          type: 'draft_email',
          draft: {
            to,
            subject,
            body
          },
          state: 'review'
        }
      };
    }

    // Check for email-related queries in Spanish
    const emailQuery = query.toLowerCase();
    const emailKeywords = [
      'correo', 'email', 'e-mail', 'mensaje', 'recibido', 'llegado', 'tienes',
      'tengo', 'hay', 'nuevo', 'nuevos', 'recibiste', 'llegaron', 'tienes mensajes',
      'tienes correos', 'tienes emails', 'tienes e-mails', 'tienes mensajes nuevos',
      'tienes correos nuevos', 'tienes emails nuevos', 'tienes e-mails nuevos',
      'has recibido', 'han llegado', 'hay nuevos'
    ];
    
    const isEmailQuery = emailKeywords.some(keyword => emailQuery.includes(keyword)) ||
                      /(cu[aá]nto|cu[aá]ntos|hay)\s+(correo|email|e[- ]?mail|mensaje)s?/i.test(query);
    
    if (isEmailQuery) {
      const emails = await fetchEmailsAction();
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const todaysEmails = emails.filter(email => {
        const emailDate = new Date(email.receivedAt);
        emailDate.setHours(0, 0, 0, 0);
        return emailDate.getTime() === today.getTime();
      });

      if (todaysEmails.length === 0) {
        return { 
          response: "No he recibido ningún correo electrónico hoy.",
          data: { emails: [] }
        };
      }
      
      // Format the response based on the number of emails
      let responseText;
      if (todaysEmails.length === 1) {
        responseText = `He recibido 1 correo hoy de ${todaysEmails[0].senderName}:\n\n`;
        responseText += `📧 ${todaysEmails[0].subject}`;
      } else {
        responseText = `He recibido ${todaysEmails.length} correos hoy:\n\n`;
        responseText += todaysEmails.map((email, index) => 
          `${index + 1}. ${email.senderName}: ${email.subject}`
        ).join('\n');
      }
      
      return { 
        response: responseText,
        data: { emails: todaysEmails }
      };
    }

    // Check for appointment-related queries
    const appointmentQuery = query.toLowerCase();
    const appointmentKeywords = [
      'cita', 'reunión', 'agenda', 'programar', 'sacar cita', 'hacer cita',
      'agendar', 'disponibilidad', 'horario', 'calendario', 'evento'
    ];
    
    const isAppointmentQuery = appointmentKeywords.some(keyword => appointmentQuery.includes(keyword)) ||
      /(programar|agendar|sacar|hacer|crear).*(cita|reuni[oó]n|evento)/i.test(query);
    
    if (isAppointmentQuery) {
      const accessToken = (session as any).accessToken as string;
      if (!accessToken) {
        return { response: "Lo siento, no puedo acceder a tu calendario sin autenticación." };
      }

      // Check for explicit confirmation to book/create the event
      const confirmKeywords = ['confirma', 'sí', 'si', 'dale', 'procede', 'agenda', 'programa', 'crea', 'hazlo'];
      const isConfirmation = confirmKeywords.some(keyword => cleanQuery.toLowerCase().startsWith(keyword)) || 
                             confirmKeywords.some(keyword => cleanQuery.toLowerCase().endsWith(keyword));

      // Try to parse appointment details from previous context if available (e.g., from a 'confirm' state)
      // This part needs to be robust: How do we get previousAppointmentData?
      // For now, assume it might come from a more complex state management or a specific query structure.
      // Let's look for a structure like "confirma la cita {JSON_DATA}" or similar
      let previousAppointmentData: Partial<AppointmentDetails> & { attendees?: string[] } | null = null;
      const jsonConfirmationMatch = query.match(/confirma(?: la cita)?\s*(\{.*\})/i);
      if (jsonConfirmationMatch && jsonConfirmationMatch[1]) {
        try {
          previousAppointmentData = JSON.parse(jsonConfirmationMatch[1]);
        } catch (e) {
          console.error("Error parsing JSON from confirmation query:", e);
        }
      }
      
      let appointment: Partial<AppointmentDetails> & { attendees?: string[] } = previousAppointmentData || {}; 
      appointment.timeZone = appointment.timeZone || 'America/Mexico_City'; // Default timezone

      if (!isConfirmation || !previousAppointmentData) {
        // If not a direct confirmation with data, parse from query as before
        const titleMatch = query.match(/para (.+?)(?: el| con| a las|$)/i);
        appointment.title = appointment.title || (titleMatch ? titleMatch[1].trim() : '');

        const dateMatch = query.match(/(?:el )?(\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4})/i) ||
                        query.match(/(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)/i);
        if (dateMatch && !appointment.date) {
          let date = new Date();
          if (dateMatch[1].includes('/') || dateMatch[1].includes('-')) {
            const [day, month, year = date.getFullYear()] = dateMatch[1].split(/[\/\-]/);
            date = new Date(Number(year), Number(month) - 1, Number(day));
          } else {
            const dayName = dateMatch[0].toLowerCase().trim();
            const days = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];
            const targetDay = days.indexOf(dayName.normalize("NFD").replace(/[\u0300-\u036f]/g, ""));
            if (targetDay !== -1) {
                const today = date.getDay();
                const diff = (targetDay - today + 7) % 7 || 7; 
                date.setDate(date.getDate() + diff);
            }
          }
          appointment.date = date.toISOString().split('T')[0];
        }

        const timeMatch = query.match(/(\d{1,2})(?::(\d{2}))?\s*(?:hrs?|horas?|:)?\s*(?:de la )?(mañana|tarde|noche)?/i);
        if (timeMatch && !appointment.time) {
          let hours = parseInt(timeMatch[1], 10);
          const minutes = timeMatch[2] ? parseInt(timeMatch[2], 10) : 0;
          const period = timeMatch[3]?.toLowerCase();
          if (period === 'tarde' || period === 'noche') {
            if (hours < 12) hours += 12;
          } else if (period === 'mañana' && hours === 12) { // 12am is 00 hours
            hours = 0;
          } else if (period === 'mañana' && hours > 12) { // e.g. 13 mañana is invalid
             // Potentially handle error or clarify
          } else if ((period === 'tarde' || period === 'noche') && hours === 12) { // 12pm is 12, 12am is 0
            // Correct for 12pm, no change needed if hours is already 12 for PM
          } else if (!period && hours < 9) { // Heuristic: if no period and early morning, assume AM unless past 12pm logic hit
             // if 7 without am/pm, likely 7am not 7pm (19:00)
          }
          appointment.time = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
        }

        const durationMatch = query.match(/(?:por|de|durante)\s+(\d+)\s+(minutos?|horas?)/i);
        if (durationMatch && !appointment.duration) {
            const value = parseInt(durationMatch[1], 10);
            const unit = durationMatch[2].startsWith('min') ? 'minutes' : 'hours';
            appointment.duration = unit === 'minutes' ? value : value * 60;
        } else if (!appointment.duration) {
            appointment.duration = 30; // Default duration if not specified
        }

        // Extract potential attendee email from the query if not already present (e.g. "agenda con juan@example.com")
        const attendeeEmailMatch = query.match(/(?:con|para)\s+([\w.-]+@[\w.-]+\.[a-zA-Z]{2,})/i);
        if (attendeeEmailMatch && attendeeEmailMatch[1]) {
            if (!appointment.attendees) appointment.attendees = [];
            if (!appointment.attendees.includes(attendeeEmailMatch[1])) {
                appointment.attendees.push(attendeeEmailMatch[1]);
            }
        } else {
            // If we are replying to an email, the sender of that email is the client.
            // This requires `handleAssistantQuery` to be aware of the email context if it's a reply.
            // For now, let's assume `name` (parsed earlier for new emails) might hold a client name,
            // and `to` (parsed for new emails) might hold their email if the context is new.
            // This is a simplification; a more robust solution would pass email context explicitly.
            const clientEmailForAppointment = cleanQuery.match(/para\s+([\w\s]+)\scon\s+correo\s+([\w.-]+@[\w.-]+\.[a-zA-Z]{2,})/i);
            if(clientEmailForAppointment && clientEmailForAppointment[2]) {
                 if (!appointment.attendees) appointment.attendees = [];
                 if (!appointment.attendees.includes(clientEmailForAppointment[2])) {
                    appointment.attendees.push(clientEmailForAppointment[2]);
                }
            }
            // If no specific attendee is mentioned, and this is a new appointment request (not a reply to a client),
            // it might be for the user themselves, or they need to specify.
            // If `to` was parsed earlier for an email draft, that could be the client.
            else if (to && !appointment.attendees?.includes(to)) { // 'to' here is the email parsed for new email drafts
                 if (!appointment.attendees) appointment.attendees = [];
                 appointment.attendees.push(to);
            }
        }
      }
      
      const validationError = validateAppointment(appointment as AppointmentDetails);
      if (validationError) {
        return {
          response: validationError,
          data: { type: 'appointment', state: 'needs_info', appointment, missingInfo: [validationError] }
        };
      }

      // We have all basic info, now check for conflicts or create if confirmed
      const fullAppointmentDetails = appointment as AppointmentDetails;
      const appointmentDateObj = new Date(`${fullAppointmentDetails.date}T${fullAppointmentDetails.time}:00`);
      const startTimeISO = appointmentDateObj.toISOString();
      const endTimeISO = new Date(appointmentDateObj.getTime() + fullAppointmentDetails.duration * 60000).toISOString();

      if (isConfirmation && previousAppointmentData) { // User confirmed a previously proposed slot
        // Double check conflicts before creating, even if previously clear
        const conflictCheck = await checkCalendarConflicts(accessToken, startTimeISO, endTimeISO, fullAppointmentDetails.timeZone);
        if (conflictCheck.hasConflict) {
          return {
            response: `Lo siento, parece que ahora hay un conflicto para el ${format(parseISO(fullAppointmentDetails.date), 'PPPP', { locale: es })} a las ${fullAppointmentDetails.time}. Ya tienes un evento llamado "${conflictCheck.conflictingEvents?.[0]?.summary}". ¿Quieres que intentemos con otra hora?`,
            data: { type: 'appointment', state: 'conflict', appointment: fullAppointmentDetails }
          };
        }
        
        // If client email is not in attendees, try to add it (e.g. from `to` variable if it was a direct command)
        if (to && fullAppointmentDetails.attendees && !fullAppointmentDetails.attendees.includes(to)) {
             fullAppointmentDetails.attendees.push(to);
        }

        const result = await createCalendarEvent(accessToken, fullAppointmentDetails);
        if (result.success) {
          let successMessage = `¡Perfecto! He agendado "${fullAppointmentDetails.title}" para el ${format(parseISO(fullAppointmentDetails.date), 'PPPP', { locale: es })} a las ${fullAppointmentDetails.time}.`;
          if (fullAppointmentDetails.attendees && fullAppointmentDetails.attendees.length > 0) {
            successMessage += ` Se ha enviado una invitación a: ${fullAppointmentDetails.attendees.join(', ')}.`;
          } else {
            successMessage += " He creado el evento en tu calendario.";
          }
          return {
            response: successMessage,
            data: { type: 'appointment', state: 'scheduled', event: result.event }
          };
        } else {
          return {
            response: `Hubo un error al crear el evento: ${result.error}. Por favor, inténtalo de nuevo.`,
            data: { type: 'appointment', state: 'error', appointment: fullAppointmentDetails }
          };
        }
      } else {
        // This is a new request, or we still need to confirm. Check conflicts first.
        const conflictCheck = await checkCalendarConflicts(accessToken, startTimeISO, endTimeISO, fullAppointmentDetails.timeZone);
        if (conflictCheck.hasConflict) {
          return {
            response: `He encontrado un conflicto para el ${format(parseISO(fullAppointmentDetails.date), 'PPPP', { locale: es })} a las ${fullAppointmentDetails.time}. Ya tienes un evento llamado "${conflictCheck.conflictingEvents?.[0]?.summary}". ¿Quieres que busque otra hora o prefieres que propongas una distinta?`,
            data: { type: 'appointment', state: 'conflict', appointment: fullAppointmentDetails, conflictingEvent: conflictCheck.conflictingEvents?.[0]?.summary }
          };
        }

        // No conflict, ask for confirmation
        // Prepare data for potential confirmation query (e.g. "sí, confirma la cita {"title":...}")
        const appointmentDataForConfirmation = JSON.stringify(fullAppointmentDetails);
        let confirmMessage = `¿Deseas que programe la cita "${fullAppointmentDetails.title}" para el ${format(parseISO(fullAppointmentDetails.date), 'PPPP', { locale: es })} a las ${fullAppointmentDetails.time}?`;
        if (fullAppointmentDetails.attendees && fullAppointmentDetails.attendees.length > 0) {
          confirmMessage += ` Se enviará una invitación a: ${fullAppointmentDetails.attendees.join(', ')}.`;
        }
        return {
          response: confirmMessage + ` (Puedes decir: "sí, confirma la cita ${appointmentDataForConfirmation}")`,
          data: {
            type: 'appointment',
            state: 'confirm',
            appointment: fullAppointmentDetails
          }
        };
      }
    }

    // Default response for other queries
    return { 
      response: "Lo siento, no he entendido tu solicitud. ¿Podrías ser más específico?" 
    };

  } catch (error) {
    console.error("Error in handleAssistantQuery:", error);
    return { 
      response: "Lo siento, ha ocurrido un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde." 
    };
  }
};

export const suggestEmailResponseAction = async (email: { emailId: string; senderName: string; senderEmail: string; userContext?: string }) => {
  const session = await getServerSession(authOptions);
  if (!session || !session.user) {
    console.error("Unauthorized access to suggestEmailResponseAction");
    // Consistent error handling for unauthorized access
    return { suggestedResponse: "Lo siento, necesitas iniciar sesión para realizar esta acción." };
  }

  const accessToken = (session as any).accessToken as string;
  if (!accessToken) {
    console.error("Access token not found in session for suggestEmailResponseAction");
    return { suggestedResponse: "Error de autenticación: No se encontró el token de acceso." };
  }
  
  try {
    // Directly call the Genkit flow for suggesting email responses
    const flowInput: SuggestEmailResponseInput = {
      emailId: email.emailId,
      accessToken: accessToken, // Pass the access token to fetch email content
      senderName: email.senderName,
      senderEmail: email.senderEmail,
      userContext: email.userContext,
      // emailContent is optional if emailId and accessToken are provided, the flow will fetch it
    };

    const result = await suggestEmailResponse(flowInput);

    return { suggestedResponse: result.suggestedResponse };

  } catch (error) {
    console.error("Error in suggestEmailResponseAction when calling suggestEmailResponse flow:", error);
    // Provide a user-friendly error message in Spanish
    let errorMessage = "Lo siento, no pude generar una respuesta en este momento. Por favor, inténtalo de nuevo más tarde.";
    if (error instanceof Error) {
      // Potentially log more specific errors or customize message based on error type
      // For now, a generic message is fine, but you could check e.g., error.message.includes('fetch')
    }
    return { 
      suggestedResponse: errorMessage 
    };
  }
};
