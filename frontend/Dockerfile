# Alvo escolhido por RUN_MODE no docker-compose.yml (build.target).

# RUN_MODE=dev: Metro sobre o workspace do Code Server (hot reload).
FROM node:22-alpine AS dev
WORKDIR /workspace/frontend
EXPOSE 8081
CMD ["sh", "-c", "npm install && npx expo start --web --port 8081"]

# RUN_MODE=server: build web estático a partir da branch.
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG EXPO_PUBLIC_API_URL
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL
RUN npx expo export --platform web

FROM nginx:1.27-alpine AS server
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8081
CMD ["nginx", "-g", "daemon off;"]
