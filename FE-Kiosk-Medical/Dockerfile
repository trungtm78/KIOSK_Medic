# ===== Stage 1: Build =====
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Cài dependencies
RUN npm install

# Copy toàn bộ source
COPY . .

# Build Next.js (xuất ra .next)
RUN NEXT_DISABLE_ESLINT=1 npm run build


# ===== Stage 2: Run =====
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy từ build stage
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./

# Cài các dependency cần thiết cho production
RUN npm install --omit=dev

# CSO Finding #5 - run as non-root user (Alpine syntax)
RUN addgroup -S app && adduser -S -G app -h /app -s /sbin/nologin appuser \
    && chown -R appuser:app /app
USER appuser

# Expose cổng chạy app
EXPOSE 3000

# Lệnh khởi động
CMD ["npm", "start"]
