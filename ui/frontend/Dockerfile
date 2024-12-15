# ui/frontend/react-app/Dockerfile

# Stage 1: Build React app
FROM node:16-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . ./
RUN npm run build

# Stage 2: Serve app with Nginx
FROM nginx:1.23-alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy built React app from Stage 1
COPY --from=build /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
