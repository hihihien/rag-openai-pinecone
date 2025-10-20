/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: { unoptimized: true }, // for <img src> without Next/Image optimization
  trailingSlash: true,           // ensures folder-style export
  basePath: '/archiv/2026-MMI-KI-Chatbot',                  // no subpath
  assetPrefix: '/archiv/2026-MMI-KI-Chatbot/',             // use relative paths
  env: {
    NEXT_PUBLIC_BASE_PATH: '/archiv/2026-MMI-KI-Chatbot',
    NEXT_PUBLIC_API_URL: 'https://rag-openai-pinecone.onrender.com'
  },
};

export default nextConfig;
