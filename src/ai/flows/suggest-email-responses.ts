'use server';

/**
 * @fileOverview An AI agent that suggests email responses to client inquiries.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';
import { google, gmail_v1 } from 'googleapis'; // Import google and specific Gmail types

// Helper function to recursively extract all plain text content from Gmail message payload
function extractAllTextPartsRecursive(payload: gmail_v1.Schema$MessagePart | undefined, depth = 0): string[] {
  if (!payload || depth > 10) return []; // Max depth to prevent infinite loops
  let textSnippets: string[] = [];

  if (payload.mimeType === 'text/plain' && payload.body?.data) {
    try {
      const decodedContent = Buffer.from(payload.body.data, 'base64').toString('utf-8').trim();
      if (decodedContent) { // Only add if non-empty after trimming
        textSnippets.push(decodedContent);
      }
    } catch (e) {
      console.error("Error decoding base64 content in email part:", e);
      // Optionally, log or handle a placeholder if decoding fails
    }
  }

  // Recursively process sub-parts
  if (payload.parts && payload.parts.length > 0) {
    for (const part of payload.parts) {
      textSnippets = textSnippets.concat(extractAllTextPartsRecursive(part, depth + 1));
    }
  }
  return textSnippets;
}

// Main function to initiate extraction and join collected snippets
function extractEmailContent(payload: gmail_v1.Schema$MessagePart | undefined): string {
  if (!payload) return '';
  const allTextSnippets = extractAllTextPartsRecursive(payload);
  // Join collected snippets. If no substantive text parts were found, this will be an empty string.
  return allTextSnippets.join('\n\n');
}

const SuggestEmailResponseInputSchema = z.object({
  emailContent: z.string().optional().describe('The content of the email to respond to. Used if emailId and accessToken are not provided or fetching fails.'),
  senderName: z.string().describe('The name of the sender of the email.'),
  senderEmail: z.string().describe('The email address of the sender.'),
  userContext: z
    .string()
    .optional()
    .describe('Any relevant context about the user or the email.'),
  accessToken: z.string().optional().describe('Optional: Google Access Token for API access. Required if using emailId.'),
  emailId: z.string().optional().describe('Optional: The ID of the email to fetch content for. Requires accessToken.'),
}).refine(data => {
  // If emailId is provided, accessToken must also be provided.
  if (data.emailId && !data.accessToken) {
    return false;
  }
  // If emailContent is not provided, then emailId and accessToken must be.
  if (!data.emailContent && (!data.emailId || !data.accessToken)) {
    return false;
  }
  return true;
}, {
  message: "If emailId is provided, accessToken is required. If emailContent is not provided, emailId and accessToken are required for fetching.",
});

export type SuggestEmailResponseInput = z.infer<typeof SuggestEmailResponseInputSchema>;

const SuggestEmailResponseOutputSchema = z.object({
  suggestedResponse: z.string().describe('The suggested response to the email.'),
  fetchedEmailId: z.string().optional().describe('The ID of the email if its content was fetched.'),
});
export type SuggestEmailResponseOutput = z.infer<typeof SuggestEmailResponseOutputSchema>;

export async function suggestEmailResponse(
  input: SuggestEmailResponseInput
): Promise<SuggestEmailResponseOutput> {
  return suggestEmailResponseFlow(input);
}

const DATANALISIS_IO_CONTEXT = `
Datanalisis.io – Contexto Corporativo y Propuesta de Valor
Resumen:
Datanalisis.io es una empresa especializada en proveer soluciones avanzadas de Inteligencia de Negocios (BI) e Inteligencia Artificial (AI), orientada a que las organizaciones alcancen mayor claridad operativa, automatización de procesos y una toma de decisiones verdaderamente basada en datos. Nuestro objetivo es que los líderes empresariales tengan control total sobre sus operaciones, aprovechando al máximo la información existente y nueva para generar valor, eficiencia y ventajas competitivas sostenibles.

¿Quiénes Somos?
En Datanalisis.io nos posicionamos como el socio tecnológico estratégico para organizaciones modernas que buscan transformar sus operaciones y la forma en que toman decisiones. Nuestro equipo se especializa en la integración de herramientas de BI y AI sofisticadas, alineándolas con los flujos de trabajo actuales de cada cliente para optimizar el rendimiento organizacional.
La metodología que aplicamos está basada en el uso práctico de la analítica y la automatización, garantizando que cada proyecto tenga impacto directo en los resultados del negocio.

Expertos en Transformación: Nos especializamos en rediseñar modelos operativos y marcos de decisión mediante la implementación de dashboards, reportes personalizados y automatización inteligente.

Integración de Datos: Tenemos la capacidad de integrar fuentes de datos diversas en la organización, eliminando silos y ofreciendo una visión integral y accionable.

Generación de Valor: No solo entregamos reportes; identificamos eficiencias ocultas, mejoramos procesos y descubrimos ventajas competitivas a partir de los activos de datos existentes.

Portafolio de Servicios
Datanalisis.io ofrece un portafolio integral de servicios diseñados para las necesidades actuales y futuras de las empresas:

1. Soluciones de Inteligencia de Negocios (BI)
Desarrollo e implementación de dashboards y herramientas de reportes para monitoreo y análisis en tiempo real.
Consolidación de datos de múltiples áreas para una visión transversal: operaciones, finanzas, ventas, recursos humanos, etc.
Seguimiento de KPIs, benchmarking de desempeño y analítica predictiva para la gestión proactiva.

2. Inteligencia Artificial (AI) para Automatización de Procesos y Servicios
Implementación de agentes inteligentes para la captación de prospectos y atención al cliente, mejorando la velocidad y personalización de las interacciones.
Automatización inteligente de procesos clave del negocio, incluyendo:
Facturación
Órdenes de Compra
Órdenes de Servicio
Optimización de procesos basada en AI para reducir la carga manual, eliminar redundancias y aumentar la fiabilidad y velocidad de ejecución.

3. Desarrollo de BI por Departamento
Soluciones BI adaptadas a áreas críticas:
Recursos Humanos: Analítica de personal, seguimiento de ausentismo, optimización de talento.
Cobros: Monitoreo de cuentas por cobrar, tendencias de pago, gestión de riesgo.
Contabilidad: Dashboards financieros en tiempo real, monitoreo de cumplimiento, conciliaciones automáticas.
Marketing: Analítica de campañas, segmentación de clientes, análisis de ROI.

Ventajas Competitivas y Beneficios Clave
Toma de Decisiones Basada en Datos: Proveemos información relevante, oportuna y accionable para empoderar a directivos y mandos medios.
Automatización Integral: Con el uso de AI, ayudamos a nuestros clientes a agilizar procesos complejos y liberar recursos humanos para tareas de mayor valor.
Valor Sostenible: Vamos más allá de la tecnología, ayudando a incorporar la cultura analítica y la automatización como parte integral del ADN organizacional.
Implementación Centrada en el Cliente: Nuestras soluciones se personalizan según la realidad y los requerimientos de cada organización, garantizando pertinencia y retorno de inversión (ROI) medible.

¿Por Qué Elegir a Datanalisis.io?
No somos solo un proveedor tecnológico, sino un aliado estratégico en la transformación digital. Nos diferenciamos por:
Experiencia Probada: Trayectoria comprobada en la implementación exitosa de soluciones BI y AI en múltiples industrias.
Acompañamiento Directo: Compromiso con el éxito del cliente mediante soporte continuo y mejora constante de las soluciones.
Escalabilidad: Soluciones preparadas para crecer con el cliente, acompañando tanto necesidades actuales como futuras.
Fiabilidad: Enfoque en implementaciones robustas, seguras y alineadas a normativas, protegiendo la integridad de los datos y el cumplimiento regulatorio.
`;

// The prompt itself only needs the email content, sender details, and user context.
// The flow will handle preparing this data.
const suggestEmailResponsePrompt = ai.definePrompt({
  name: 'suggestEmailResponsePrompt',
  input: { schema: z.object({
    actualEmailContent: z.string(),
    senderName: z.string(),
    senderEmail: z.string(),
    userContext: z.string().optional(),
  })},
  output: {schema: SuggestEmailResponseOutputSchema}, // Output only suggestedResponse
  prompt: `Eres un asistente de IA de Datanalisis.io ayudando al usuario a responder correos de clientes.

Contexto sobre Datanalisis.io:
${DATANALISIS_IO_CONTEXT}

El usuario ha recibido el siguiente correo:
De: {{{senderName}}} <{{{senderEmail}}}>
Contenido: {{{actualEmailContent}}}

Contexto adicional proporcionado por el usuario: {{{userContext}}}

Por favor, sugiere una respuesta apropiada y profesional al correo del cliente.
Utiliza la información del contexto sobre Datanalisis.io para responder cualquier pregunta sobre nuestros productos, servicios o propuesta de valor.
Si el correo del cliente es una pregunta general o no está directamente relacionada con los servicios de Datanalisis.io, responde de manera útil y cortés.
Si el correo es muy simple (ej. "Gracias", "OK"), sugiere una respuesta breve y educada.
Asegúrate de mantener un tono profesional y servicial en todo momento.
Si la consulta del cliente es compleja o requiere información que no está en el contexto provisto, sugiere coordinar una llamada o solicitar más detalles para ofrecer una respuesta completa.
Al final de tu respuesta, si has proporcionado información sobre los servicios de Datanalisis.io, pregunta amablemente al cliente si le gustaría agendar una reunión para discutir sus necesidades con más detalle.
NO incluyas la información de contacto (Correo, Teléfono, Redes Sociales) en la respuesta, a menos que el cliente la solicite explícitamente.`,
});

// Check if the email is a general greeting or simple message
function isGeneralEmail(content: string): boolean {
  const contentLower = content.toLowerCase();
  const simpleGreetings = [
    'hola', 'buenos días', 'buenas tardes', 'buenas noches',
    'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
    'cómo estás', 'cómo está', 'cómo te va', 'qué tal',
    'how are you', 'how is it going', 'what\'s up', 'probando', 'test', 'prueba',
    'gracias', 'ok', 'okay', 'perfecto', 'excelente', 'de acuerdo', 'entendido'
  ];
  
  // Check for very short messages or simple acknowledgments
  if (contentLower.split(/\\s+/).length <= 5) {
    // Further check if it's just a simple thank you or acknowledgment
    if (simpleGreetings.some(greeting => contentLower.includes(greeting))) {
        return true;
    }
  }
  return false; // Default to false if not clearly a general/simple email
}

const suggestEmailResponseFlow = ai.defineFlow(
  {
    name: 'suggestEmailResponseFlow',
    inputSchema: SuggestEmailResponseInputSchema,
    outputSchema: SuggestEmailResponseOutputSchema,
  },
  async (input: SuggestEmailResponseInput) => {
    let contentForPrompt = input.emailContent || '';
    let fetchedEmailId: string | undefined = undefined;

    if (input.emailId && input.accessToken) {
      console.log(`Suggest Response: Fetching email with ID: ${input.emailId}`);
      try {
        const oauth2Client = new google.auth.OAuth2();
        oauth2Client.setCredentials({ access_token: input.accessToken });
        const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

        const emailDetailsResponse = await gmail.users.messages.get({
          userId: 'me',
          id: input.emailId,
          format: 'full',
        });
        
        const message = emailDetailsResponse.data;
        const fetchedContent = extractEmailContent(message.payload);
        fetchedEmailId = message.id ?? undefined;

        if (fetchedContent) {
          contentForPrompt = fetchedContent;
          console.log(`Suggest Response: Successfully fetched content for email ID: ${input.emailId}`);
        } else {
          console.warn(`Suggest Response: Could not extract plain text content for email ID: ${input.emailId}. Falling back to provided emailContent if available.`);
          if (!input.emailContent) { 
            contentForPrompt = "Could not retrieve email content.";
          }
        }
      } catch (error) {
        console.error(`Suggest Response: Error fetching email (ID: ${input.emailId}):`, error);
        if (!input.emailContent) { 
          throw new Error(`Failed to fetch email content for ID ${input.emailId} and no fallback content provided for suggestion.`);
        }
        console.warn(`Suggest Response: Falling back to provided emailContent for email ID: ${input.emailId}`);
      }
    }

    if (!contentForPrompt) {
      console.error("Suggest Response: No content available for email response suggestion.");
      return { suggestedResponse: "Error: No email content available to suggest a response." , fetchedEmailId };
    }

    console.log("DEBUG: Email content for prompt:", contentForPrompt);

    // Handle general greetings or simple emails AFTER content has been fetched/set
    if (isGeneralEmail(contentForPrompt)) {
      const responses = [
        `¡Hola ${input.senderName}! Gracias por tu mensaje. ¿Hay algo más en lo que pueda ayudarte hoy?`,
        `¡Buen día ${input.senderName}! Gracias por contactarme. Quedo a tu disposición si necesitas algo más.`,
        `¡Hola ${input.senderName}! Recibí tu mensaje. ¡Gracias!`
      ];
      // If the original email was very short and simple, provide a shorter, more direct acknowledgment.
      if (contentForPrompt.split(/\\s+/).length <= 3) {
          return { suggestedResponse: `¡Hola ${input.senderName}! Gracias por tu correo.` };
      }
      return {
        suggestedResponse: responses[Math.floor(Math.random() * responses.length)],
        fetchedEmailId
      };
    }

    const { output } = await suggestEmailResponsePrompt({
      actualEmailContent: contentForPrompt,
      senderName: input.senderName,
      senderEmail: input.senderEmail,
      userContext: input.userContext,
    });

    if (!output) {
        throw new Error("Suggest Email Response prompt did not return an output.");
    }

    return { suggestedResponse: output.suggestedResponse, fetchedEmailId };
  }
);
