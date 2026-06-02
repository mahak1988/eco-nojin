version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: econojin-backend
    restart: unless-stopped
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:econojin_pass@db:5432/econojin
      - ENABLE_DATABASE=true
      - DEBUG=false
    depends_on:
      db: { condition: service_healthy }
    networks: [econet]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: econojin-frontend
    restart: unless-stopped
    ports: ["80:80"]
    depends_on: [backend]
    networks: [econet]

  db:
    image: postgis/postgis:17-3.5
    container_name: econojin-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: econojin
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: econojin_pass
    volumes: [pgdata:/var/lib/postgresql/data]
    ports: ["5432:5432"]
    networks: [econet]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  econet: { driver: bridge }

volumes:
  pgdata: