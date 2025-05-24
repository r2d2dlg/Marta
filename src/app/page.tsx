
import { redirect } from 'next/navigation';

export default function HomePage() {
  redirect('/inbox');
  return null; // Or a loading spinner, but redirect should be fast
}
