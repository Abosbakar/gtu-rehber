# Ön yüz derlenir ve nginx ile sunulur (geliştirme sunucusu kullanılmaz)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json .npmrc ./
RUN npm ci && test -x node_modules/.bin/vite
COPY . .
# Tarayıcının API'ye ulaşacağı adres derleme sırasında gömülür
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
