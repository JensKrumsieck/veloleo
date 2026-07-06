ARG NODE_VERSION=24
FROM node:${NODE_VERSION}-alpine AS builder
WORKDIR /app

RUN npm install -g vite

COPY dashboard /app/dashboard
COPY data /app/data

WORKDIR /app/dashboard
RUN npm ci
RUN npm run build

FROM node:${NODE_VERSION}-alpine
ENV NODE_ENV=production

WORKDIR /app/dashboard
COPY --from=builder /app/dashboard/package*.json ./
RUN npm ci --omit=dev

# copy build folders
COPY --from=builder /app/dashboard/build ./build
COPY --from=builder /app/dashboard/.svelte-kit ./.svelte-kit
COPY --from=builder /app/data ../data

RUN chown -R node:node /app
USER node

EXPOSE 3000

ENV DATA_DIR=/app/data

ENTRYPOINT ["node", "build"]