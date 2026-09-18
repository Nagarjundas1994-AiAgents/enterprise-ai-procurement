/** @type {import('next').NextConfig} */
const BACKEND = process.env.CAP_BACKEND_URL || "http://localhost:4004";

const nextConfig = {
  reactStrictMode: true,
  // Monorepo-adjacent layout (root + frontend lockfiles): keep tracing rooted here.
  outputFileTracingRoot: __dirname,
  // Proxy all backend calls server-side: browser -> :3000/backend/* -> :4004/*.
  // Same-origin for the browser (no CORS), custom headers forwarded as-is.
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: `${BACKEND}/:path*`
      }
    ];
  }
};

module.exports = nextConfig;
