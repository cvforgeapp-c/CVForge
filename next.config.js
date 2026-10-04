/** @type {import('next').NextConfig} */
const nextConfig = {
  distDir: 'out',
  images: { unoptimized: true },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
