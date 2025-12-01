/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true },
  trailingSlash: true,

  // new paths:
  basePath: '/2026-FBM-Web-KI-Chatbot',
  assetPrefix: '/2026-FBM-Web-KI-Chatbot/',

  env: {
    NEXT_PUBLIC_BASE_PATH: '/2026-FBM-Web-KI-Chatbot',
    NEXT_PUBLIC_API_URL: 'https://kim-chatbot.onrender.com'
  },
};

export default nextConfig;