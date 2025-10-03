import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable static exports for the `next export` command
  output: 'export',
  
  // Set the base path if your app is not served from the root
  basePath: '',
  
  // Set the asset prefix for production if needed
  assetPrefix: process.env.NODE_ENV === 'production' ? 'https://clinica.aviladevops.com.br' : '',
  
  // Enable React Strict Mode
  reactStrictMode: true,
  
  // Enable SWC minification
  swcMinify: true,
  
  // Configure images if needed
  images: {
    unoptimized: true, // Required for static exports
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL || 'https://clinica.aviladevops.com.br',
  },
};

export default nextConfig;
