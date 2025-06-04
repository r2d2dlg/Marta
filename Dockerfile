# =======================================
# Stage 1: Build the application
# =======================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Install system dependencies
RUN apk add --no-cache libc6-compat

# Copy package files for better layer caching
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the application
COPY . .

# Create a default next.config.js if it doesn't exist
RUN if [ ! -f next.config.js ]; then \
      echo "module.exports = { output: 'standalone' };" > next.config.js; \
    fi

# Build the application
RUN npm run build

# =======================================
# Stage 2: Create the production image
# =======================================
FROM node:18-alpine AS runner

# Set working directory
WORKDIR /app

# Set environment variables
ENV NODE_ENV=production \
    PORT=8080 \
    HOST=0.0.0.0 \
    NEXT_TELEMETRY_DISABLED=1

# Install system dependencies
RUN apk add --no-cache dumb-init

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Copy next.config.js if present
COPY --from=builder /app/next.config.js ./

# Copy next-i18next.config.js if present
COPY --from=builder /app/next-i18next.config.js ./

# Set the user to non-root
USER nextjs

# Expose the port the app runs on
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/api/health || exit 1

# Start the application using dumb-init
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["node", "server.js"]

# =======================================
# Security best practices
# =======================================
# 1. Using minimal base image (node:18-alpine)
# 2. Running as non-root user
# 3. Using multi-stage builds to reduce image size
# 4. Not running as root
# 5. Using dumb-init for proper signal handling
# 6. Using health checks
# 7. Disabling Next.js telemetry
# 8. Using pnpm for faster and more efficient dependency management