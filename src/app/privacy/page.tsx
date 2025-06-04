import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy - Marta',
  description: 'Privacy policy for Marta application',
};

export default function PrivacyPolicy() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
      <p className="text-gray-600 mb-6">Last updated: May 20, 2025</p>
      
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">1. Information We Collect</h2>
        <p className="mb-4">
          When you sign in with Google, we collect the following information:
        </p>
        <ul className="list-disc pl-6 mb-4 space-y-2">
          <li>Your name</li>
          <li>Email address</li>
          <li>Profile picture URL</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">2. How We Use Your Information</h2>
        <p className="mb-4">
          We use the information we collect to:
        </p>
        <ul className="list-disc pl-6 mb-4 space-y-2">
          <li>Provide and maintain our service</li>
          <li>Authenticate your account</li>
          <li>Send you important service-related communications</li>
          <li>Improve our services</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">3. Data Security</h2>
        <p className="mb-4">
          We implement appropriate security measures to protect your personal information. However,
          no method of transmission over the Internet or electronic storage is 100% secure.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">4. Third-Party Services</h2>
        <p className="mb-4">
          Our service uses Google OAuth for authentication. By using our service, you agree to
          Google's <a href="https://policies.google.com/privacy" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Privacy Policy</a> and <a href="https://policies.google.com/terms" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">Terms of Service</a>.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">5. Changes to This Policy</h2>
        <p>
          We may update our Privacy Policy from time to time. We will notify you of any changes by
          posting the new Privacy Policy on this page.
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4">6. Contact Us</h2>
        <p>
          If you have any questions about this Privacy Policy, please contact us at afdelaguardia@gmail.com
        </p>
      </section>
    </div>
  );
}
