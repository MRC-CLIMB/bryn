# Bryn server provisioning notes

Any templates referred to can be found in the deploy_tools/config_templates directory of the repo.

Make sure 443 is open in security group for new server.

### Required packages:

- nginx
- Python >= 3.8
- Git
- pip
- python3-venv
- certbot (letsencrypt)
- nodejs + npm

##### Notes:

- Alias python to python3
  ** add `alias python=python3` and `alias pip=pip3` to `~/.bash_aliases`
  ** source `~/.bash_aliases`

### Nginx

- Copy `nginx.conf` template to `/etc/nginx/`
- Copy `ssl-params.conf` template to `/etc/nginx/snippets`
- Copy `bryn.climb.ac.uk` template to `/etc/nginx/sites-available`
- `ln -s /etc/nginx/sites-available/bryn.climb.ac.uk /etc/nginx/sites-enabled/bryn.climb.ac.uk`
- disable default site `rm /etc/nginx/sites-enabled/default`
- `mkdir /tmp/letsencrypt`
- `cd /etc/ssl/certs`
- `openssl dhparam -out dhparam.pem 4096`

##### If transferring from existing server:

- copy existing letsencrypt certs:
  - copy `fullchain.pem` and `privkey.pem` from `/etc/letsencrypt/live/` on existing server (follow symlinks)
  - to `/etc/nginx/ssl/bryn.climb.ac.uk` on new server
  - edit `/etc/nginx/sites-available/bryn.climb.ac.uk` to point at temp certs in `/etc/nginx/ssl/bryn.climb.ac.uk`
  - once DNS has been changed, you can proceed to setup letsencrypt

##### If starting from scratch (DNS already points at new server)

- `sudo certbot certonly -a webroot --webroot-path=/tmp/letsencrypt -d bryn.climb.ac.uk`

##### Check nginx config is valid:

- `nginx -t`

### Gunicorn

- copy template to `/etc/systemd/system/gunicorn-bryn.climb.ac.uk.service`
- `mkdir /var/log/gunicorn`, ubuntu user has write permissions
- `sudo systemctl enable gunicorn-bryn.climb.ac.uk`
- `sudo systemctl start gunicorn-bryn.climb.ac.uk`
- Check log in `/var/log/gunicorn/`

### Setup Django site

##### On server:

- `mkdir -p ~/sites/bryn.climb.ac.uk`

##### On local machine:

- `pip install fabric`
- Clone the repo from https://github.com/MRC-CLIMB/bryn
- Obtain local settings files (from previous server, or Nick)
  1. `~/sites/bryn.climb.ac.uk/brynweb/locals.py`
  2. `~/sites/bryn.climb.ac.uk/openstack/auth_settings.py`
- from local deploy_tools dir:
  - **If DNS still points at previous server, add new ip to your hosts file before proceeding**
  - Don't just use the ip of the new server, since the fabric script makes use of the hostname
  - `fab -H ubuntu@bryn.climb.ac.uk deploy`
  - This should clone repo to remote machine, setup venv, install requirements, build frontend, consolidate static files etc.

##### On server:

- Overwrite `~/sites/bryn.climb.ac.uk/brynweb/db.sqlite3` with latest copy from existing server
- `sudo systemctl restart gunicorn-bryn.climb.ac.uk`
- `sudo service nginx restart`

### Setup letsencrypt (after DNS change)

- `sudo certbot certonly -a webroot --webroot-path=/tmp/letsencrypt -d bryn.climb.ac.uk`
- edit `/etc/nginx/sites-available/bryn.climb.ac.uk` to point at certs in `/etc/letsencrypt/live/bryn.climb.ac.uk`
