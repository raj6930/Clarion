# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Generate self-signed cert for local dev
RUN apk add --no-cache openssl && \
    mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout /etc/nginx/ssl/clarion.key \
      -out /etc/nginx/ssl/clarion.crt \
      -subj "/CN=localhost/O=Clarion/C=AU" && \
    apk del openssl

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
