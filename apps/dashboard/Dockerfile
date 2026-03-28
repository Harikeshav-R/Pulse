FROM node:20-alpine

WORKDIR /app

# Enable pnpm
RUN corepack enable pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install

# Copy application files
COPY . .

# Build application (optional, we use dev server for hackathon)
# RUN pnpm run build

# Expose port for dev server
EXPOSE 5173

# Start Vite dev server bound to all interfaces
CMD ["pnpm", "run", "dev", "--host", "0.0.0.0"]
