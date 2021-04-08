<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/MRC-CLIMB/bryn">
    <img src="brynweb/static/images/climb_logo.png?raw=true" alt="MRC Climb Logo" height="80">
  </a>

  <h3 align="center">Bryn</h3>

  <p align="center">
    The CLIMB-BIG-DATA web management interface
    <!-- <br />
    <a href="https://github.com/MRC-CLIMB/bryn/wiki"><strong>Explore the docs »</strong></a> -->
    <br />
    <br />
    <a href="https://bryn.climb.ac.uk/">Login</a>
    ·
    <a href="https://github.com/MRC-CLIMB/bryn/issues">Report Bug</a>
    ·
    <a href="https://github.com/MRC-CLIMB/bryn/issues">Request Feature</a>
  </p>
</p>

<!-- ABOUT THE PROJECT -->

## About The Project

The CLIMB-BIG-DATA project (Cloud Infrastructure for Big Data Microbial Bioinformatics) is a collaboration between Warwick, Birmingham, Cardiff, Swansea, Bath and Leicester Universities, the MRC Unit the Gambia at the London School of Hygiene and Tropical Medicine and the Quadram Institute Bioscience.

CLIMB-BIG-DATA is an ambitious 5-year initiative to deliver a cutting-edge scalable and dynamic bioinformatics platform to support academic research groups, government agencies and health service facing the challenges of big data in modern microbiology. We provide cloud-based compute, storage, and analysis tools for microbiologists across the UK, accompanied by a wide range of bioinformatics training activities.

Bryn is the web management interface for CLIMB-BIG-DATA, supporting the following:

- Team & user registration
- Server (VM) management
- Server leasing and renewals
- Volume management
- SSH Keypair management
- Team management (memberships, invitations & licencing)
- User management

### Built With

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue 3](https://v3.vuejs.org/)
- [Openstack Python API bindings](https://www.openstack.org/)

<!-- ARCHITECTURE OVERVIEW -->

## Stack Overview

Bryn predominantly uses Vue 3 on the frontend, with Django + Django Rest Framework on the backend.

The backend uses Django 3.1, leveraging vanilla Django views & templates for authentication, password reset & registration.
All API views use Django REST Framework.

The frontend uses Vue 3 (installed with vue-cli) with two entrypoints/pages:

- The first `frontend/src/base.js` (template `frontend/public/base.html`) serves as the Django base template, which is extended by all 'vanilla' Django templates.
- The second `frontend/src/main.js` (template `frontend/public/index.html`) serves as the entrypoint for the main Vue SPA.

See `frontend/vue.config.js` for further details.

<!-- GETTING STARTED -->

## Getting Started (local development)

### Prerequestites:

1. Python >= 3.8
2. npm
3. Credentials for Openstack, or a local test deployment
4. You'll need to create `brynweb/brynweb/locals.py` & `brynweb/openstack/auth_settings.py` from their respective templates.

### Setup Local Dev Environment:

#### Backend:

1. clone the repo
   ```sh
   git clone https://github.com/MRC-CLIMB/bryn
   ```
2. setup a python virtualenv (however you wish)
3. install requirements
   ```sh
   pip install -r requirements.txt
   ```
4. setup Git hooks (Black, flake 8)
   ```sh
   pre-commit install
   ```
5. start the Django dev server
   ```sh
   cd brynweb
   python manage.py runserver
   ```

#### Frontend (in a separate terminal):

1. Navigate to frontend dir
   ```sh
   cd brynweb/frontend
   ```
2. Install JS dependencies & build frontend
   ```sh
   npm install && npm run build
   ```
3. Start webpack dev server (with HMR)
   ```sh
   npm run serve
   ```

Note: if you are working from home, you're probably not whitelisted for the Openstack APIs at the various sites. The simplest solution is to tunnel through a whitelisted VM within the CLIMB network, if you wish to test against live API endpoints:

- In a separate teminal: `sshuttle --dns -H -r user@someVMwithinCLIMB 0/0`

Now, `http://localhost:8080` should give you hot module reloading. Any non-vue routes will be automatically proxied to the django dev server on port 8000. You can find the config for this in `frontend/vue.config.js`

<!-- DEPLOYMENT -->

## Deployment

See [provisioning_notes](deploy_tools/provisioning_notes.md)

<!-- LICENSE -->

## License

Distributed under GPLv3. See [LICENSE](LICENCE) for more information.
