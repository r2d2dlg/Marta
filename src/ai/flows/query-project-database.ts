'use server';
/**
 * @fileOverview A flow to query project documentation using local data.
 */

import { z } from 'zod';
import { ai } from '../genkit';
import { promises as fs } from 'fs';
import path from 'path';

// Define input and output schemas
const QueryInputSchema = z.string().describe('User query about the project.');
export type QueryInput = z.infer<typeof QueryInputSchema>;

const QueryOutputSchema = z.string().describe('Answer based on project documentation.');
export type QueryOutput = z.infer<typeof QueryOutputSchema>;

// Simple in-memory cache for the vector data
let vectorDataCache: any[] | null = null;

async function loadVectorData() {
  if (vectorDataCache) return vectorDataCache;
  
  const dataPath = path.join(process.cwd(), 'data', 'vertex_ai_vector_data.jsonl');
  console.log('Attempting to load vector data from:', dataPath);
  
  try {
    // Check if file exists and is accessible
    try {
      await fs.access(dataPath, fs.constants.R_OK);
    } catch (error) {
      const accessError = error as NodeJS.ErrnoException;
      console.error('File access error:', {
        code: accessError.code,
        path: dataPath,
        cwd: process.cwd(),
        error: accessError.message
      });
      throw new Error(`Cannot access vector data file: ${accessError.message}`);
    }
    
    // Read file stats
    const stats = await fs.stat(dataPath);
    console.log(`File size: ${(stats.size / (1024 * 1024)).toFixed(2)} MB`);
    
    // Read the file in chunks for large files
    const chunkSize = 10 * 1024 * 1024; // 10MB chunks
    const fileHandle = await fs.open(dataPath, 'r');
    let position = 0;
    let buffer = Buffer.alloc(0);
    let lineBuffer = '';
    vectorDataCache = [];
    
    try {
      console.log('Starting to parse vector data file...');
      
      while (position < stats.size) {
        const chunk = Buffer.alloc(Math.min(chunkSize, stats.size - position));
        const { bytesRead } = await fileHandle.read(chunk, 0, chunk.length, position);
        
        if (bytesRead === 0) break;
        
        // Combine with any remaining data from previous chunk
        buffer = Buffer.concat([buffer, chunk.slice(0, bytesRead)]);
        
        // Process complete lines from the buffer
        let newlineIndex;
        while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
          const line = buffer.slice(0, newlineIndex).toString('utf8');
          buffer = buffer.slice(newlineIndex + 1);
          
          // Combine with any partial line from previous chunk
          const fullLine = lineBuffer + line;
          lineBuffer = '';
          
          if (!fullLine.trim()) continue;
          
          try {
            const data = JSON.parse(fullLine);
            vectorDataCache.push(data);
          } catch (error) {
            console.error('Error parsing JSON line:', error);
            // Store partial line for next chunk
            lineBuffer = fullLine;
          }
        }
        
        position += bytesRead;
        console.log(`Processed ${((position / stats.size) * 100).toFixed(1)}% of file...`);
      }
      
      // Process any remaining line
      if (lineBuffer.trim()) {
        try {
          const data = JSON.parse(lineBuffer);
          vectorDataCache.push(data);
        } catch (error) {
          console.error('Error parsing final JSON line:', error);
        }
      }
      
      if (vectorDataCache.length === 0) {
        throw new Error('No valid data found in the vector data file');
      }
      
      console.log(`Successfully loaded ${vectorDataCache.length} vector data entries`);
      return vectorDataCache;
      
    } finally {
      await fileHandle.close();
    }
    
  } catch (error) {
    const err = error as NodeJS.ErrnoException;
    console.error('Error in loadVectorData:', {
      message: err.message,
      stack: err.stack,
      code: err.code,
      path: dataPath
    });
    throw new Error(`Failed to load local vector data: ${err.message}`);
  }
}


export async function queryProjectDatabase(input: QueryInput): Promise<QueryOutput> {
  return queryProjectDatabaseFlow(input);
}

// Check if the query is a general greeting or simple email
function isGeneralGreeting(query: string): boolean {
  const greetings = [
    'hola', 'buenos días', 'buenas tardes', 'buenas noches',
    'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'
  ];
  
  const simplePhrases = [
    'cómo estás', 'cómo está', 'cómo te va', 'qué tal',
    'how are you', 'how is it going', 'what\'s up'
  ];
  
  const queryLower = query.toLowerCase();
  
  // Check for very short queries
  if (queryLower.split(/\s+/).length <= 3) {
    return true;
  }
  
  // Check for greetings or simple phrases
  return greetings.some(greeting => queryLower.startsWith(greeting)) ||
         simplePhrases.some(phrase => queryLower.includes(phrase));
}

// Check if the query is about company projects
function isAboutCompanyProjects(query: string): boolean {
  const projectKeywords = [
    'proyecto', 'proyectos', 'empresa', 'trabajo', 'servicio', 'servicios',
    'producto', 'productos', 'solución', 'soluciones', 'cliente', 'clientes',
    'necesito información sobre', 'información de', 'qué ofrecen', 'qué hacen',
    'veterinaria neuman', 'datos de contacto', 'contactar', 'cotización',
    'presupuesto', 'precio', 'precios', 'costo', 'costos'
  ];
  
  const queryLower = query.toLowerCase();
  return projectKeywords.some(keyword => queryLower.includes(keyword));
}

export const queryProjectDatabaseFlow = ai.defineFlow(
  {
    name: 'queryProjectDatabaseFlow',
    inputSchema: QueryInputSchema,
    outputSchema: QueryOutputSchema,
  },
  async (query) => {
    console.log('Starting queryProjectDatabaseFlow with query:', query);
    
    // Handle general greetings or simple emails
    if (isGeneralGreeting(query)) {
      const greetings = [
        '¡Hola! Soy Marta, tu asistente profesional. ¿En qué puedo ayudarte hoy?',
        '¡Buen día! Estoy aquí para apoyarte en lo que necesites. ¿Cómo puedo asistirte?',
        '¡Hola! Gracias por contactarme. Estoy lista para ayudarte con cualquier consulta o gestión que requieras.',
        '¡Hola! ¿En qué puedo ayudarte hoy? Estoy a tu disposición.'
      ];
      return greetings[Math.floor(Math.random() * greetings.length)];
    }
    
    // If the query is not about company projects, respond as a general assistant
    if (!isAboutCompanyProjects(query)) {
      const assistantResponses = [
        '¿Hay algo específico sobre tus proyectos o agenda en lo que pueda ayudarte?',
        'Estoy aquí para apoyarte en la gestión de tus tareas, correos o citas. ¿Cómo puedo asistirte?',
        'Si tienes alguna consulta sobre tus proyectos, agenda o comunicaciones, no dudes en decírmelo.',
        '¿Te gustaría que te ayude a organizar tu día o responder algún correo? Estoy para servirte.'
      ];
      return assistantResponses[Math.floor(Math.random() * assistantResponses.length)];
    }
    
    try {
      // Load the local vector data
      console.log('Loading vector data...');
      const vectorData = await loadVectorData();
      console.log(`Loaded ${vectorData.length} vector data entries`);
      
      if (!vectorData || vectorData.length === 0) {
        console.error('No vector data available');
        return 'No pude cargar la información de la documentación. Por favor, inténtalo de nuevo más tarde.';
      }
      
      // Enhanced search functionality
      const queryLower = query.toLowerCase();
      console.log('Processing question:', query);
      
      // Extract key terms from the query
      const keyTerms = queryLower
        .split(/\s+/)
        .filter(term => term.length > 3 && !['que', 'cual', 'como', 'donde', 'cuando', 'quien'].includes(term))
        .map(term => term.replace(/[^a-z0-9áéíóúüñ]/g, ''));
      
      console.log('Extracted key terms:', keyTerms);
      
      // Find documents that match the query
      const matchingDocs = vectorData
        .map(doc => {
          try {
            const docText = JSON.stringify(doc).toLowerCase();
            // Calculate a simple relevance score
            const score = keyTerms.reduce((total, term) => {
              return total + (docText.includes(term) ? 1 : 0);
            }, 0);
            
            return { doc, score };
          } catch (error) {
            console.error('Error processing document:', error);
            return { doc: null, score: -1 };
          }
        })
        .filter(({ score }) => score > 0)  // Only keep documents with at least one match
        .sort((a, b) => b.score - a.score)  // Sort by relevance
        .slice(0, 3)  // Limit to top 3 most relevant
        .map(({ doc }) => doc);  // Extract the documents
      
      console.log(`Found ${matchingDocs.length} matching documents`);
      
      if (matchingDocs.length === 0) {
        const noMatchResponses = [
          'No encontré información específica sobre el proyecto de Veterinaria Neuman en la documentación. ' +
          '¿Podrías proporcionar más detalles o hacer una pregunta más específica?',
          'No tengo registros específicos sobre el proyecto de Veterinaria Neuman. ' +
          '¿Hay algún aspecto en particular sobre el que te gustaría saber más?',
          'Por el momento no cuento con información detallada sobre el proyecto de Veterinaria Neuman. ' +
          '¿Hay algo más en lo que pueda ayudarte?'
        ];
        return noMatchResponses[Math.floor(Math.random() * noMatchResponses.length)];
      }
      
      // Generate a natural response based on the query
      const greetings = [
        '¡Hola!',
        '¡Buen día!',
        '¡Hola! Gracias por tu consulta.',
        '¡Claro!'
      ];
      
      const responses = [
        'Aquí tienes la información que encontré:',
        'Según los registros, esto es lo que encontré:',
        'He revisado la documentación y esto es lo que puedo contarte:',
        'De acuerdo con la información disponible:'
      ];
      
      const greetings2 = [
        'Espero que esta información te sea útil.',
        '¿Neitas algo más?',
        '¿Hay algo más en lo que pueda ayudarte?',
        '¿Te gustaría saber algo más sobre este tema?'
      ];
      
      const greeting = greetings[Math.floor(Math.random() * greetings.length)];
      const responseIntro = responses[Math.floor(Math.random() * responses.length)];
      const greeting2 = greetings2[Math.floor(Math.random() * greetings2.length)];
      
      // Extract and format the relevant information
      const responseDetails = matchingDocs
        .filter(doc => doc && (doc.content || doc.text || doc.descripcion || doc.descripción))
        .map(doc => {
          // Try to find the most relevant content field
          let content = doc.content || doc.text || doc.descripcion || doc.descripción || '';
          
          // Clean up the content
          content = content
            .replace(/\n+/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
            
          // If it's a product, try to include the name and description
          let productInfo = '';
          if (doc.nombre || doc.name) {
            productInfo = `*${doc.nombre || doc.name}*: `;
          }
          
          // Extract first 2-3 sentences if content is long
          const sentences = content.match(/[^.!?]+[.!?]+/g) || [content];
          let relevantContent = sentences.slice(0, 3).join(' ');
          
          // If still too long, truncate
          if (relevantContent.length > 300) {
            relevantContent = relevantContent.substring(0, 300) + '...';
          }
          
          return productInfo + relevantContent;
        })
        .filter(content => content.trim().length > 0)
        .join('\n\n');
      
      // Combine into a friendly response
      let response = `${greeting} ${responseIntro}\n\n${responseDetails}`;
      
      // Add a closing if we have content
      if (responseDetails) {
        response += `\n\n${greeting2}`;
      } else {
        // If no content was found, provide a helpful response
        response = `No encontré información específica sobre "${query}" en los registros. `;
        response += '¿Podrías reformular tu pregunta o proporcionar más detalles?';
      }
      
      console.log('Generated response with length:', response.length);
      return response;
      
    } catch (error) {
      const err = error as Error;
      console.error('Error in queryProjectDatabaseFlow:', {
        message: err.message,
        stack: err.stack,
        query: query
      });
      
      if (err.message.includes('ENOMEM') || err.message.includes('allocation failed')) {
        return 'La documentación es demasiado grande para procesar. Por favor, intenta con una búsqueda más específica o contacta al soporte.';
      }
      
      const errorResponses = [
        'Ocurrió un error al buscar en la documentación. Por favor, inténtalo de nuevo más tarde.',
        'Lo siento, hubo un problema al procesar tu solicitud. Por favor, inténtalo nuevamente en unos momentos.',
        'Vaya, parece que hubo un error inesperado. ¿Podrías intentar con otra pregunta o más tarde?'
      ];
      return errorResponses[Math.floor(Math.random() * errorResponses.length)];
      return 'Error: Failed to query project documentation. Please check the logs for more details.';
    }
  }
);
