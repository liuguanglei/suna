import type { NextConfig } from 'next';


// let nextConfig: NextConfig = {
//   allowedDevOrigins: ['127.0.0.1', 'localhost', '192.168.10.81', '10.18.144.205'],

//   webpack: (config) => {
//     // This rule prevents issues with pdf.js and canvas
//     config.externals = [...(config.externals || []), { canvas: 'canvas' }];

//     // Ensure node native modules are ignored
//     config.resolve.fallback = {
//       ...config.resolve.fallback,
//       canvas: false,
//     };

//     return config;
//   },
// };

// if (process.env.NEXT_PUBLIC_VERCEL_ENV === 'production') {
//   nextConfig = withSentryConfig(nextConfig, {
//     org: 'kortix-ai',
//     project: 'suna-nextjs',
//     silent: !process.env.CI,
//     widenClientFileUpload: true,
//     tunnelRoute: '/monitoring',
//     disableLogger: true,
//     automaticVercelMonitors: true,
//   });
// }

const nextConfig = (): NextConfig => ({
  output: (process.env.NEXT_OUTPUT as 'standalone') || undefined,
});

export default nextConfig;
