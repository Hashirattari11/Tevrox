/** @type {import('next').NextConfig} */
const nextConfig = {
  // Turbopack configuration for @/ aliases
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  // Set an empty turbopack config so Next 16 does not treat the old webpack
  // config as required migration material.
  turbopack: {},
};

module.exports = nextConfig;
