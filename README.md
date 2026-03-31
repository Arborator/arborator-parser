# arborator-parser

The backend parsing engine for [ArboratorGrew](https://arboratorgrew.elizia.net). A Flask + Celery REST API that wraps [BertForDeprel](https://github.com/kirianguiller/BertForDeprel) for dependency parsing.

## Architecture

```
Quick_parsing (Flask frontend)  ──HTTP──▶  arborator-parser (Flask + Celery backend)  ──▶  BertForDeprel
   - text tokenization                      - model management on disk
   - file upload UI                         - Celery task queue (train / parse)
   - proxies requests to backend            - writes CoNLL-U, invokes BertForDeprel
```

- **[Quick_parsing](https://github.com/Arborator/Quick_parsing)** is the user-facing frontend. It tokenizes text into CoNLL-U format and proxies all parsing/training requests via HTTP to this backend. It does not modify CoNLL-U content.
- **arborator-parser** (this repo) is the backend. It manages model files, runs BertForDeprel training and inference as Celery tasks, and returns parsed CoNLL-U.
- The frontend sends `X-Application-Models: quick_parser` in request headers to select the flat model store used by Quick_parsing.

### Gloss parser support

When a model's `project_name` starts with `gloss_`, the `parse_sentences` Celery task automatically performs a Gloss↔FORM swap:

1. **Pre-processing:** For each token with `Gloss=X` in MISC, the original FORM is saved as `OrigForm=` in MISC and replaced with the gloss value. This lets BertForDeprel parse using English glosses instead of surface forms.
2. **Post-processing:** After parsing, the original FORM is restored from `OrigForm=` and the gloss is placed back in `Gloss=` in MISC. All predicted annotations (HEAD, DEPREL, UPOS, etc.) are preserved.

This is implemented in `app/utils_gloss.py` and called from `app/models/celery_tasks.py`.

## Set in production

### Cloning the project

- Clone server with submodules

```bash
# with ssh (git might ask you to set ssh key for the project)
git clone --recurse-submodules git@github.com:Arborator/arborator-parser.git

# or with http
git clone --recurse-submodules https://github.com/Arborator/arborator-parser
```

### Installing dependencies

#### Install Redis

Check the doc on the [official doc of redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/)

```
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
```

### Installing the two python virtual environment

- Install venv as you can (on the LISN machine, we need to set miniconda3 vens)

#### The server venv

```bash
# if using conda/miniconda
conda create -n parser-venv python=3.8
conda activate parser-venv
pip install -r requirements.txt
# you might need to have a C compiler, if so, `
sudo apt install build-essential
# and this dependency for uwsgi
sudo apt-get install libxcrypt-dev

# if using python-venv
python3.8 -m venv parser-venv
```

#### The venv for BertForDeprel

TODO : Document this part

### Start the services

```bash
# if the dir does not exist
mkdir -p ~/.config/systemd/user/

# then link the service and enable it
ln arborator-parser.service /etc/systemd/system
systemctl enable arborator-parser.service
systemctl start arborator-parser.service
```

- Create service for user Celery app (can't use system-wise service as arboratorgrew is not root). The template of the service is at the root of this repo.

```bash
ln arborator-parser-celery.service ~/.config/systemd/user/
systemctl enable arborator-parser-celery.service
systemctl start arborator-parser-celery.service
```

Add the nginx server block conf file. Again, it can be found at the root of this repo.

## Where are the logs and status ?

### Nginx logs

```bash
# access logs :
sudo tail -f /var/log/nginx/access.log
# and error logs :
sudo tail -f /var/log/nginx/error.log
```

### Services status

All service logging :

```
journalctl -f
```

And our services logs :

```bash
# for flask app
systemctl status arborator-parser.service
# and for celery app
systemctl status arborator-parser-celery.service
```

### Application logs

Logs of arborator-parser (from root of this repo)

```bash
# live tail of the flask logs
tail -f ./logs/arborator-parser.log

# live tail of celery service logs, added to the previous 100 lines
journalctl --unit=arborator-parser-celery.service -f -n 100
```

## Some Key info

### Production version

- PORT : 8002
- Path : /home/arboratorgrew/arborator-parser/wsgi.py
- PATH_MODELS : /home/arboratorgrew/arborator-parser_models/
- specific config files : arborator-parser-celery.service ; arborator-parser-celery.service ; arborator-parser.ini ; arborator-parser.nginx.conf ;
- socket : arborator-parser.sock

### Development version

/!\ Don't install the dev server on the same user as the prod server. Indeed, the dev and prod version of celery will collide.

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
curl localhost:8002/parser/healthy
# or
curl localhost:8012/parser/healthy
```

## API doc

If port tunneling to server, you can access to the doc by going on the URL : https://127.0.0.1:8088/parser/doc

## Checkèserver

To be sure that the server is always running, we added systemctl timer

### check the `check_server.sh` script is correct

it should check the server healthy endpoint, and restart the arborator-parser.service and arborator-parser-celery.service

Make sure the script is executable with

```
chmod +x /path/to/your/script.sh
```

### add a service in ~/.config/systemd/user

template of the service is in this repo under the name check_server.service. It should point to the correct check_server.sh script

### add a timer in ~/.config/systemd/user

template of the timer is in this repo under the name check_server.service. It should point to the correct check_server.service

### enable the service and the timer

```
systemctl --user daemon-reload
systemctl --user enable --now check_server.timer
```

### user services persistency

As we use user services, when the user session scope terminate (can be minutes, hours or days after the user leave the session), the system will stop all of the services of this user.

To prevent this, we set

```
sudo loginctl enable-linger arboratorgrew
```

### monitoring of the check_server timers/services

#### check status

```
systemctl --user status check_server.service
systemctl --user status check_server.timer
```

#### check logs

```
journalctl --unit check_server.service
journalctl --unit check_server.timer
```
