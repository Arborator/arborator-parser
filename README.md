# arborator-parser

## Set in production
- Clone server with submodules 
```bash
# with ssh (git might ask you to set ssh key for the project)
git clone --recurse-submodules git@github.com:Arborator/arborator-parser.git

# or with http
git clone --recurse-submodules https://github.com/Arborator/arborator-parser
```

- Install venv as you can (on the LISN machine, we need to set miniconda3 vens)

```bash
# if using conda/miniconda
conda create -n parser-venv python=3.8

# if using python-venv
python3.8 -m venv parser-venv
```

- Create service for user arboratorgrew (can't use system-wise service as arboratorgrew is not root). The template of the service is at the root of this repo.

```bash
systemctl --user edit arborator-parser.service --full --force
systemctl --user enable arborator-parser.service
systemctl --user start arborator-parser.service
```

- Create service for user Celery app (can't use system-wise service as arboratorgrew is not root). The template of the service is at the root of this repo.

```bash
systemctl --user edit arborator-parser-celery.service --full --force
systemctl --user enable arborator-parser-celery.service
systemctl --user start arborator-parser-celery.service
```

Add the nginx server block conf file. Again, it can be found at the root of this repo.

## Where are the logs ?
Machine wise nginx log :
```bash
# access logs :
sudo tail -f /var/log/nginx/access.log
# and error logs :
sudo tail -f /var/log/nginx/error.log
```

User wise service logging : 
```
journalctl --user -f
```


Status of the service :
```bash
# for flask app
systemctl --user status arborator-parser.service
# and for celery app
systemctl --user status arborator-parser-celery.service
```

Logs of arborator-parser (from root of this repo)
```
tail -f ./logs/arborator-parser.log
journalctl --user-unit=arborator-parser-celery.service -f
```

# Production version
- PORT : 8002
- Path : /home/arboratorgrew/arborator-parser/wsgi.py
- PATH_MODELS : /home/arboratorgrew/arborator-parser_models/
- specific config files : arborator-parser-celery.service ; arborator-parser-celery.service ; arborator-parser.ini ; arborator-parser.nginx.conf ; 
- socket : arborator-parser.sock

## Development version
- PORT : 8001
- Path : /home/arboratorgrew/arborator-parser_dev/wsgi.py
- PATH_MODELS : /home/arboratorgrew/arborator-parser_models_dev/
- specific config files : arborator-parser-celery.service ; arborator-parser-celery_dev.service ; arborator-parser_dev.ini ; arborator-parser_dev.nginx.conf ; 
- socket : arborator-parser_dev.sock
- It's using the same reddis port as the production server, we want to change that to have each of them using their own instance of reddis.


## How to debug ?
First check all the logs mentioned above

Then, check healthyness : On the server, do the following curl :
```bash
curl http://127.0.0.1:8088/parser/healthy
```

## API doc
If port tunneling to server, you can access to the doc by going on the URL : https://127.0.0.1:8088/parser/doc

