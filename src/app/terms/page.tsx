import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Terms of Service - Marta',
  description: 'Terms of service for Marta application',
};

export default function TermsOfService() {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
      <p className="text-gray-600 mb-6">Last updated: May 20, 2025</p>
      
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">1. Acceptance of Terms</h2>
        <p className="mb-4">
          By accessing or using the Marta application, you agree to be bound by these Terms of Service.
          If you do not agree with any part of these terms, you may not use our service.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">2. Use of Service</h2>
        <p className="mb-4">You agree to use the service only for lawful purposes and in accordance with these Terms.</p>
        <p className="mb-4">You agree not to:</p>
        <ul className="list-disc pl-6 mb-4 space-y-2">
          <li>Use the service in any way that violates any applicable laws or regulations</li>
          <li>Engage in any activity that interferes with or disrupts the service</li>
          <li>Attempt to gain unauthorized access to any part of the service</li>
          <li>Use the service to transmit any malicious code or harmful content</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">3. User Accounts</h2>
        <p className="mb-4">
          When you create an account with us, you must provide accurate and complete information.
          You are responsible for maintaining the confidentiality of your account credentials.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">4. Intellectual Property</h2>
        <p className="mb-4">
          The service and its original content, features, and functionality are owned by us and are
          protected by international copyright, trademark, and other intellectual property laws.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">5. Limitation of Liability</h2>
        <p className="mb-4">
          In no event shall we be liable for any indirect, incidental, special, consequential, or
          punitive damages arising out of or in connection with your use of the service.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">6. Changes to Terms</h2>
        <p className="mb-4">
          We reserve the right to modify or replace these Terms at any time. We will provide notice
          of any changes by updating the "Last updated" date at the top of these Terms.
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4">7. Contact Us</h2>
        <p>
          If you have any questions about these Terms, please contact us at afdelaguardia@gmail.com
        </p>
      </section>
    </div>
  );
}
