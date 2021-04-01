#Simple tinder app with Postgres, Gunicorn, and Nginx

add .env.dev; .env.prod; .env.db to source root

docker-compose up -d --build and go to http://localhost:8000
(local)

docker-compose -f docker-compose.prod.yml up -d --build and go to http://localhost:1337
(production)