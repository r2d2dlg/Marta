'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Calendar, Clock, User, Check, X } from 'lucide-react';
import { format, parseISO, isToday, isTomorrow, addDays } from 'date-fns';
import { es } from 'date-fns/locale';
import { AppointmentDetails } from '@/types/calendar';

export function ChatInterface() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string, data?: any}>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [appointment, setAppointment] = useState<Partial<AppointmentDetails>>({});
  const [appointmentStep, setAppointmentStep] = useState<'idle' | 'title' | 'date' | 'time' | 'confirm'>('idle');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [draftEmail, setDraftEmail] = useState<any>(null);
  const [showDraftModal, setShowDraftModal] = useState(false);
  const [draftEdit, setDraftEdit] = useState<any>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle new assistant messages for draft email
  useEffect(() => {
    const lastMsg = messages[messages.length - 1];
    if (lastMsg?.data?.type === 'draft_email') {
      setDraftEmail(lastMsg.data.draft);
      setDraftEdit(lastMsg.data.draft);
      setShowDraftModal(true);
    }
  }, [messages]);

  // Handle appointment scheduling flow
  const handleAppointmentStep = async (data: any) => {
    if (data?.type === 'appointment') {
      if (data.state === 'needs_info') {
        setAppointment(data.appointment);
        setAppointmentStep('title');
      } else if (data.state === 'confirm') {
        setAppointment(data.appointment);
        setAppointmentStep('confirm');
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const userMessage = message;
    setMessage('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: userMessage,
          appointment: appointmentStep !== 'idle' ? { ...appointment, currentStep: appointmentStep } : undefined
        }),
      });

      if (!response.ok) {
        throw new Error('Error processing your request');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response,
        data: data.data
      }]);
      
      // Handle any appointment scheduling flow
      if (data.data) {
        await handleAppointmentStep(data.data);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Lo siento, ha ocurrido un error al procesar tu solicitud.' 
      }]);
      setAppointmentStep('idle');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle appointment confirmation
  const handleConfirmAppointment = async (confirmed: boolean) => {
    if (!confirmed) {
      setAppointmentStep('idle');
      setAppointment({});
      setMessages(prev => [...prev, { 
        role: 'user', 
        content: 'No, gracias.' 
      }]);
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch('/api/calendar/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          appointment: {
            ...appointment,
            duration: 30, // Default 30 minutes
            timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
          }
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `✅ Cita programada exitosamente. ${data.message}`,
          data: { type: 'appointment_success', event: data.event }
        }]);
      } else {
        throw new Error(data.error || 'Error al programar la cita');
      }
    } catch (error: any) {
      console.error('Error creating calendar event:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `❌ No se pudo programar la cita: ${error.message}`
      }]);
    } finally {
      setIsLoading(false);
      setAppointmentStep('idle');
      setAppointment({});
    }
  };

  // Format date for display
  const formatDisplayDate = (dateString: string) => {
    const date = new Date(dateString);
    if (isToday(date)) return 'hoy';
    if (isTomorrow(date)) return 'mañana';
    return format(date, "EEEE d 'de' MMMM", { locale: es });
  };

  // Render appointment form based on current step
  const renderAppointmentForm = () => {
    if (appointmentStep === 'idle') return null;

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value } = e.target;
      setAppointment(prev => ({
        ...prev,
        [name]: name === 'duration' ? parseInt(value, 10) : value
      }));
    };

    const handleNextStep = () => {
      if (appointmentStep === 'title' && appointment.title) {
        setAppointmentStep('date');
      } else if (appointmentStep === 'date' && appointment.date) {
        setAppointmentStep('time');
      } else if (appointmentStep === 'time' && appointment.time) {
        setAppointmentStep('confirm');
      }
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-semibold mb-4">
            {appointmentStep === 'title' && '¿Sobre qué es la cita?'}
            {appointmentStep === 'date' && '¿Qué día te gustaría agendarla?'}
            {appointmentStep === 'time' && '¿A qué hora?'}
            {appointmentStep === 'confirm' && 'Confirma los detalles'}
          </h3>

          <div className="space-y-4">
            {appointmentStep === 'title' && (
              <div>
                <input
                  type="text"
                  name="title"
                  value={appointment.title || ''}
                  onChange={handleInputChange}
                  placeholder="Ej: Reunión de seguimiento"
                  className="w-full p-2 border rounded"
                  autoFocus
                />
              </div>
            )}

            {appointmentStep === 'date' && (
              <div className="space-y-2">
                {[0, 1, 2, 3, 4, 5, 6].map(daysToAdd => {
                  const date = addDays(new Date(), daysToAdd);
                  const dateStr = date.toISOString().split('T')[0];
                  const isSelected = appointment.date === dateStr;
                  
                  return (
                    <button
                      key={dateStr}
                      type="button"
                      onClick={() => {
                        setAppointment(prev => ({ ...prev, date: dateStr }));
                        setTimeout(() => document.getElementById('time-input')?.focus(), 100);
                      }}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        isSelected 
                          ? 'bg-blue-100 border-blue-500' 
                          : 'hover:bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className="flex items-center">
                        <div className="w-10 h-10 flex items-center justify-center rounded-full mr-3 bg-blue-500 text-white">
                          <Calendar size={20} />
                        </div>
                        <div>
                          <div className="font-medium">
                            {format(date, 'EEEE', { locale: es })}
                            {daysToAdd === 0 && ' (hoy)'}
                            {daysToAdd === 1 && ' (mañana)'}
                          </div>
                          <div className="text-sm text-gray-500">
                            {format(date, 'd \'de\' MMMM', { locale: es })}
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {appointmentStep === 'time' && (
              <div className="flex items-center space-x-4">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Clock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="time-input"
                    type="time"
                    name="time"
                    value={appointment.time || ''}
                    onChange={handleInputChange}
                    className="block w-full pl-10 p-2 border rounded"
                    required
                  />
                </div>
                <div className="flex-1">
                  <select
                    name="duration"
                    value={appointment.duration || 30}
                    onChange={handleInputChange}
                    className="w-full p-2 border rounded"
                  >
                    <option value="30">30 minutos</option>
                    <option value="60">1 hora</option>
                    <option value="90">1.5 horas</option>
                    <option value="120">2 horas</option>
                  </select>
                </div>
              </div>
            )}

            {appointmentStep === 'confirm' && appointment.date && appointment.time && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium mb-2">Detalles de la cita:</h4>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 mr-2 text-blue-500" />
                    <span>{formatDisplayDate(appointment.date)}</span>
                  </div>
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-2 text-blue-500" />
                    <span>{appointment.time} - {calculateEndTime(appointment.time, appointment.duration || 30)}</span>
                  </div>
                  {appointment.title && (
                    <div className="flex items-center">
                      <User className="h-4 w-4 mr-2 text-blue-500" />
                      <span>{appointment.title}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => {
                setAppointmentStep('idle');
                setAppointment({});
              }}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded"
            >
              Cancelar
            </button>
            
            {appointmentStep !== 'confirm' ? (
              <button
                type="button"
                onClick={handleNextStep}
                disabled={
                  (appointmentStep === 'title' && !appointment.title) ||
                  (appointmentStep === 'date' && !appointment.date) ||
                  (appointmentStep === 'time' && !appointment.time)
                }
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => handleConfirmAppointment(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded"
                >
                  No, modificar
                </button>
                <button
                  type="button"
                  onClick={() => handleConfirmAppointment(true)}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded hover:bg-green-700 flex items-center"
                >
                  <Check className="h-4 w-4 mr-1" />
                  Confirmar cita
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Helper function to calculate end time
  const calculateEndTime = (startTime: string, duration: number) => {
    const [hours, minutes] = startTime.split(':').map(Number);
    const startDate = new Date();
    startDate.setHours(hours, minutes, 0, 0);
    const endDate = new Date(startDate.getTime() + duration * 60000);
    return format(endDate, 'HH:mm');
  };

  // Send the draft email
  const handleSendDraftEmail = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/email/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(draftEdit),
      });
      const data = await response.json();
      if (data.success) {
        setMessages(prev => [...prev, { role: 'assistant', content: '✅ El correo ha sido enviado exitosamente.' }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: `❌ No se pudo enviar el correo: ${data.error || 'Error desconocido.'}` }]);
      }
    } catch (error: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Error al enviar el correo: ${error.message}` }]);
    } finally {
      setShowDraftModal(false);
      setDraftEmail(null);
      setDraftEdit(null);
      setIsLoading(false);
    }
  };

  // Render draft email modal
  const renderDraftEmailModal = () => {
    if (!showDraftModal || !draftEdit) return null;
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-lg">
          <h3 className="text-lg font-semibold mb-4">Revisar borrador de correo</h3>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium">Para:</label>
              <input type="email" className="w-full border rounded p-2" value={draftEdit.to} onChange={e => setDraftEdit({ ...draftEdit, to: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium">Asunto:</label>
              <input type="text" className="w-full border rounded p-2" value={draftEdit.subject} onChange={e => setDraftEdit({ ...draftEdit, subject: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium">Mensaje:</label>
              <textarea className="w-full border rounded p-2 min-h-[120px]" value={draftEdit.body} onChange={e => setDraftEdit({ ...draftEdit, body: e.target.value })} />
            </div>
          </div>
          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => { setShowDraftModal(false); setDraftEmail(null); setDraftEdit(null); }}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded"
            >
              Descartar
            </button>
            <button
              type="button"
              onClick={handleSendDraftEmail}
              className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded hover:bg-green-700"
              disabled={isLoading}
            >
              {isLoading ? 'Enviando...' : 'Aprobar y enviar'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="flex-1 p-4 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500">
            <p>Envíame un mensaje para comenzar...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, index) => (
              <div 
                key={index} 
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div 
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {msg.content.split('\n').map((line, i) => (
                    <p key={i} className="whitespace-pre-wrap">{line}</p>
                  ))}
                  
                  {/* Show appointment details if available */}
                  {msg.data?.type === 'appointment' && msg.data.appointment && (
                    <div className="mt-2 p-2 bg-white bg-opacity-20 rounded text-sm">
                      <div className="font-medium">{msg.data.appointment.title}</div>
                      <div>{msg.data.appointment.date} a las {msg.data.appointment.time}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                  </div>
                </div>
              </div>
            )}
            
            {/* Scroll to bottom ref */}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Appointment form modal */}
      {appointmentStep !== 'idle' && renderAppointmentForm()}
      
      {renderDraftEmailModal()}
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Escribe tu mensaje..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className="p-2 text-white bg-blue-600 rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
