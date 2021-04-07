# Simple tinder app 
with Postgres, Gunicorn, Nginx docker. This application looks like tinder which can send peoples in dependence of your subscribe(without front)
with testing which cover all functions. Custom auth with chips of simple-jwt

# Steps of start this applicaiton:
1) add .env.dev; .env.prod; .env.db; .env.prod.db to source root
2) docker-compose up -d --build and go to http://localhost:8000 (local)
3) docker-compose -f docker-compose.prod.yml up -d --build and go to http://localhost:1337 (production)

If in production run this command in console:
1) docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
2) docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
3) docker-compose -f docker-compose.prod.yml exec web python manage.py test


# main libraries:
1) Postgres
2) Gunicorn
3) djangorestframework
4) djangorestframework-simplejwt


# date the code was written: 06.04.2021
