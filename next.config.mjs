import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    middleware: {
      runtime: 'nodejs',
    },
  },
  distDir: '.next',
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'picsum.photos',
        port: '',
        pathname: '/**', 
      },
    ],
  },
  webpack: (config, { isServer }) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      module: false,
      net: false,
      dns: false,
      child_process: false,
      tls: false,
    };

    // Add these lines to suppress specific warnings
    config.ignoreWarnings = [
      { module: /opentelemetry/ },
      { file: /node_modules\/handlebars/ },
    ];

    return config;
  },
  // Add rewrites for auth
  async rewrites() {
    return [
      {
        source: '/api/auth/:path*',
        destination: '/api/auth/:path*',
      },
    ];
  },
  // Add CORS headers to API responses
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ],
      },
    ];
  },

};

// Development-specific configurations
if (process.env.NODE_ENV === 'development') {
  console.log('Running in development mode');
  
  // Enable more detailed logging in development
  nextConfig.logging = {
    fetches: {
      fullUrl: true,
    },
  };
  
  // Disable telemetry in development
  process.env.NEXT_TELEMETRY_DISABLED = '1';
} else {
  // Production configuration
  console.log('Running in production mode');
  
  // Disable telemetry in production
  process.env.NEXT_TELEMETRY_DISABLED = '1';
  
  // Add production-specific configurations
  nextConfig.compiler = {
    ...nextConfig.compiler,
    reactRemoveProperties: true,
    removeConsole: {
      exclude: ['error'],
    },
  };
}

export default nextConfig;