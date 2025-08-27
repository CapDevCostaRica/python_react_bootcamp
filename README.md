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

## Creating database migrations

This will only work for apps created using backend/contributors/capdevcr/boilerplate

After updating the `backend/contributors/your_username/your_app_name/models.py` adding or updating the table(s), follow the next steps:

1. Ensure docker is running with the containers from this project.
2. Go to `backend/contributors/your_username/your_app_name`.
3. Execute `alembic revision --autogenerate -m "some-meaningful message"`
4. Optional: review the file created under `backend/contributors/your_username/your_app_name/alembic/versions`
5. Run `alembic upgrade head` to execute the changes on the DB.
6. Optional: if you need to downgrade for some reason your change (instead of just recreate the image/container 🤯), run `alembic downgrade <hash-from-upgrade-cmd>`

## (Deprecated) Creating database migrations the legacy way

After updating the `backend/contributors//models.py` adding or updating the table(s), follow the next steps:

1. Ensure docker is running with the containers from this project.
2. Go to `backend/framework`.
3. Execute `alembic revision --autogenerate -m "some-meaningful message"`
4. Optional: review the file created under `backend/framework/alembic/versions`
5. Run `alembic upgrade head` to execute the changes on the DB.
6. Optional: if you need to downgrade for some reason your change (instead of just recreate the image/container 🤯), run `alembic downgrade <hash-from-upgrade-cmd>`

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.  
See the [LICENSE.txt](./LICENSE.txt) file for details or visit:  
https://creativecommons.org/licenses/by-nc/4.0/legalcode.txt


