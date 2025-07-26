/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Enable React Strict Mode
  reactStrictMode: true,
  // Enable server actions (if using Next.js 13+)
  // Configure images if needed
  images: {
    domains: ['lh3.googleusercontent.com'], // Add other domains as needed
  },
  // Environment variables that should be available to the client
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
  // Add webpack configuration if needed
  webpack: (config, { isServer }) => {
    // Add any webpack configuration here
    return config;
  },
};

module.exports = nextConfig;
