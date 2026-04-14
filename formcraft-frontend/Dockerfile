FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG BUILD_ENV=production
RUN npm run build -- --configuration=${BUILD_ENV}

FROM nginx:alpine
COPY --from=build /app/dist/formcraft-frontend/browser /usr/share/nginx/html
# Use template so BACKEND_HOST can be overridden at runtime (default: "backend" for docker-compose)
ENV BACKEND_HOST=backend
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/index.html || exit 1
