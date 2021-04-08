import random

from pathlib import Path
from fabric import task
from patchwork.files import append, exists

REPO_URL = "https://github.com/MRC-CLIMB/bryn"


@task
def deploy(c):
    """
    Deploy brynweb to specified hosts

    From the deploy_tools directory, run:
    fab -H ubuntu@wbryn.climb.ac.uk deploy
    """
    site_dir = Path(f"/home/{c.user}/sites/{c.host}")
    source_dir = site_dir / "brynweb"
    local_source_dir = Path("../brynweb")

    _create_directory_structure(c, site_dir)
    _get_latest_source(c, site_dir)
    _copy_local_settings(c, local_source_dir, source_dir)
    _update_settings(c, source_dir)
    _update_virtualenv(c, site_dir)
    _build_frontend(c, source_dir)
    _update_static_files(c, source_dir)
    _update_database(c, source_dir)
    _restart_gunicorn(c)
    _restart_nginx(c)


def _create_directory_structure(c, site_dir):
    for subdir in ("static", "venv"):
        c.run(f"mkdir -p {site_dir}/{subdir}")


def _get_latest_source(c, site_dir):
    if exists(c, site_dir / ".git"):
        c.run(f"cd {site_dir} && git fetch")
    else:
        c.run(f"git clone {REPO_URL} {site_dir}")
    current_commit = c.local("git log -n 1 --format=%H").stdout
    c.run(f"cd {site_dir} && git reset --hard {current_commit}")


def _copy_local_settings(c, local_source_dir, source_dir):
    c.put(
        str(local_source_dir / "brynweb/locals.py"),
        str(source_dir / "brynweb/locals.py"),
    )
    c.put(
        str(local_source_dir / "openstack/auth_settings.py"),
        str(source_dir / "openstack/auth_settings.py"),
    )


def _update_settings(c, source_dir):
    # Disable debug
    settings_path = source_dir / "brynweb/settings.py"
    c.run(f"sed -i 's/DEBUG = True/DEBUG = False/g' {settings_path}")

    # Set allowed hosts
    hosts_find = "ALLOWED_HOSTS =.\\+$"
    hosts_replace = f'ALLOWED_HOSTS = ["{c.host}"]'
    c.run(f"sed -i 's/{hosts_find}/{hosts_replace}/g' {settings_path}")

    # Update SITE_SCHEME
    site_scheme_find = "SITE_SCHEME =.\\+$"
    site_scheme_replace = 'SITE_SCHEME = "https"'
    c.run(f"sed -i 's/{site_scheme_find}/{site_scheme_replace}/g' {settings_path}")

    # Update SITE_DOMAIN
    site_domain_find = "SITE_DOMAIN =.\\+$"
    site_domain_replace = f'SITE_DOMAIN = "{c.host}"'
    c.run(f"sed -i 's/{site_domain_find}/{site_domain_replace}/g' {settings_path}")

    # Create and import secret key
    secret_key_path = source_dir / "brynweb/secret_key.py"
    if not exists(c, secret_key_path):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        append(c, secret_key_path, f'SECRET_KEY = "{key}"')
    append(c, settings_path, "\nfrom .secret_key import SECRET_KEY")


def _update_virtualenv(c, site_dir):
    virtualenv_dir = site_dir / "venv"
    if not exists(c, virtualenv_dir / "bin/pip"):
        c.run(f"python3 -m venv {virtualenv_dir}")
    c.run(f"{virtualenv_dir}/bin/pip install -r {site_dir}/requirements.txt")


def _build_frontend(c, source_dir):
    frontend_dir = source_dir / "frontend"
    with c.cd(str(frontend_dir)):
        c.run("npm install && npm run build")


def _update_static_files(c, source_dir):
    with c.cd(str(source_dir)):
        c.run("../venv/bin/python manage.py collectstatic --noinput")


def _update_database(c, source_dir):
    with c.cd(str(source_dir)):
        c.run("../venv/bin/python manage.py migrate --noinput")


def _restart_gunicorn(c):
    c.run(f"sudo systemctl restart gunicorn-{c.host}")


def _restart_nginx(c):
    c.run("sudo service nginx restart")
