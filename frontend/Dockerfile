FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG SITE_URL=http://localhost
ARG SITE_INDEXABLE=false
ENV SITE_URL=$SITE_URL SITE_INDEXABLE=$SITE_INDEXABLE NEXT_TELEMETRY_DISABLED=1 API_INTERNAL_URL=http://api:8000
RUN npm run build
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
