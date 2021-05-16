![example workflow](https://github.com/qaser/foodgram-project/actions/workflows/foodgram_workflow.yaml/badge.svg)

# FoodyDoody (aka Foodgram from Yandex.Praktikum)

This is an online service where users can publish recipes, subscribe to other users ' publications, add their favorite recipes to the Favorites list, and download a summary list of products needed to prepare one or more selected dishes before going to the store.

## Getting Started

This guide will help you prepare your server and deploy the application.

### Prerequisites

You must have installed on your server:
* [Docker](https://www.docker.com/get-started)
* [Docker compose](https://github.com/docker/compose)

### Installing

First of all clone repository (example commands makes in __bash__):
```
git clone https://github.com/qaser/foodgram-project.git
```
In root directory rename file *.env.example* to *.env*
```
mv .env.example .env
```

Fill in all the values in the file following the tips.

Сopy the file *.env* to your server:
```
scp .env <user_name>@<public_ip>:~
```

## Deployment

There are two ways to deploy:

__First way__

Just copy the following files to your server:

    *docker-compose.yaml*
    *nginx/* (dir)

And run command:

```
sudo docker-compose up
```

__Second way__

In the tab *Actions* on GitHub create new *workflow*.
Put the file *foodgram_workflow.yaml* in new workflow folder.

Тo work properly, you need to create several secret words 
on *Settings* tab -> *Secrets* on GitHub.

*USER* - server user

*HOST* - public ip of your server

*SSH_KEY* - ssh key

*PASSPHRASE* - secret phrase for your ssh key (if necessary) 

*TELEGRAM_TO* - you telegram id (check @userinfobot) (if necessary)

*TELEGRAM_TOKEN* - token for your telegram bot (check @BotFather) (if necessary)

If you want to create your image on the DockerHub you will need to change the *foodgram_workflow.yaml* and create secrets for DockerHub:

*DOCKER_USERNAME* - your DockerHub's profile login

*DOCKER_PASSWORD* - your DockerHub's profile password

If you want to use my image on the DockerHub delete 
*build_and_push_to_docker_hub* job on the *foodgram_workflow.yaml* file.

Initialize commit on your git repository and check *Actions* tab for deploy logs.

After deploying you must enter in web container and make some commands:
1. Check web container id:
```
docker container ls
```
2. Enter in the container:
```
docker exec -it <ID CONTAINER> bash
```
3. Create admin user:
```
python manage.py createsuperuser
```
4. Fill the database with the data from the example:

```
python manage.py loaddata fixtures.json
```

## Project work

For check:
http://84.201.153.211/

## Built With

Web application:

* [Python: ver.3.8.5](https://www.python.org/)
* [Django: ver.3.2](https://www.djangoproject.com/)
* [Django Rest Framework: ver.3.11.0](https://www.django-rest-framework.org/)
* [PyJWT:ver.1.7.1](https://pypi.org/project/PyJWT/)

Database:

* [Postgres: ver.12.4](https://www.postgresql.org/)

Server side:

* [Ubuntu: ver.20.0.4](https://ubuntu.com/)
* [Docker: ver.20.10.5](https://www.docker.com/)
* [Gunicorn: ver.20.0.4](https://gunicorn.org/)
* [Nginx: alpine](https://www.nginx.org/)

## Authors

* **Alexey Saygin** - [GitHub](https://github.com/qaser) | [DockerHub](https://hub.docker.com/r/dangerexit/)
