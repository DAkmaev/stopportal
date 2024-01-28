# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
FROM node:18.17.1 as build-stage

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG FRONTEND_ENV=production

ENV VUE_APP_ENV=${FRONTEND_ENV}

ENV NODE_OPTIONS="--openssl-legacy-provider"

RUN npm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.15

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY infra/nginx.conf /etc/nginx/conf.d/default.conf
COPY infra/nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf