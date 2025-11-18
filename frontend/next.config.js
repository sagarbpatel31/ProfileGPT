/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for free hosting platforms
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Remove rewrites and headers for static export compatibility
  // These features require server-side functionality
}

module.exports = nextConfig