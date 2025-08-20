# Important notes

In the repository, you will find an .env.example Please copy it and rename the copy to .env; this will load environmental values for Docker.

From there, you can run:

```
docker-compose up
```

If you added a new module or a new dependency remember to run

```
docker-compose up --build
```

On the first run, and if you haven't changed anything in the .env file, you can visit http://localhost:4000 and receive a random motivational phrase; your setup is working. 

If you need to reset your DB maybe you switching apps, then run

```
docker-compose run flask_app bash /app/run_local.sh reset_db
```

If you created a local environment and installed the requirements, you can reset the DB from your host as well
```
python backend/framework/scripts/reset_db.py 
```

## Doing exercises 

Please create a folder under contributors with your username. In there, you can make a new folder to create a new module, and inside that folder, create two files.

```
main.py
requirements.txt
```

Then, go to .env and change APPLICATION_FOLDER to your module, e.g., "capdevcr/health". Now, restart your Docker and your application should be running. 

If you plan to use Alembic, ensure that your alembic.ini file and folder are located in the root of your module. Additionally, you can create a seeds.py file that will run when Docker starts to populate your database. You can check framework/seeds.py as an example.

You should use a centralized database.py config file as we do on the framework for your app. 

## Accesing bash

If you need to access bash to run any commands, just use:

```
docker-compose exec flask_app bash
```
