export interface AppointmentDetails {
  title: string;
  date: string;
  time: string;
  duration: number; // in minutes
  attendees?: string[];
  description?: string;
  timeZone?: string;
}

export type AppointmentStep = 
  | 'initial'
  | 'title'
  | 'date'
  | 'time'
  | 'duration'
  | 'attendees'
  | 'confirm';

export interface AppointmentState {
  step: AppointmentStep;
  appointment: Partial<AppointmentDetails>;
  isCreating: boolean;
  error?: string;
}
