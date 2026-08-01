# Frontend Dockerfile: build static assets and serve via Nginx

# ---- Build stage ----
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install --no-audit --no-fund

# Copy source and build
COPY . .
RUN npm run build

# ---- Runtime stage ----
FROM nginx:alpine AS runtime

# Copy frontend-specific nginx config for serving static files
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
