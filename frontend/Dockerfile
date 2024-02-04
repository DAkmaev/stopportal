# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ARG FRONTEND_ENV=production
ARG API_BASE_URL=/api

ENV VUE_APP_ENV=${FRONTEND_ENV}
ENV VUE_APP_API_URL=${API_BASE_URL}

ENV NODE_OPTIONS="--openssl-legacy-provider"

RUN npm run build
RUN npm install --global http-server
#RUN cp -r dist /staticfiles/
CMD ["npx", "-y", "http-server", "-p", "8000", "dist"]

## Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
#FROM nginx:1.15
#
#COPY --from=build-stage /app/dist/ /usr/share/nginx/html
#
#COPY infra/nginx.conf /etc/nginx/conf.d/default.conf
#COPY infra/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
