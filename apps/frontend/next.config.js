/** @type {import('next').NextConfig} */
const nextConfig = {
    experimental: {
        appDir: true,
    },
    images: {
        domains: ['localhost'],
    },
    async rewrites() {
        return [
            {
                source: '/api/v1/:path*',
                destination: `${process.env.API_BASE_URL || 'http://localhost:3001'}/api/v1/:path*`,
            },
        ];
    },
};

module.exports = nextConfig;
