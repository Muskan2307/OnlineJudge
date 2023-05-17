Installation Guide:
Installation should happen on the Windows only and the version should support Docker Desktop.
1. Install Docker Desktop on your machine and it should be in running state when running/testing the code.
2. If virtualenv is not in your system.
	Command: pip install virtualenv
3. Now check your installation 
	Command: virtualenv --version
4. Download the submitted code which is expected to be a ZIP file.
5. Extract the ZIP file to a local folder
6. Initialize virtual environment in the local folder.
	Command: virtualenv venv
7. Activate the virtual environment.
	Command: venv\Scripts\activate
8. Change directory to the folder containing manage.py(i.e. src) and install requirements in the virtual environment.
	Command: pip install -r requirements.txt


For running the project:
1. For creating new superuser in the system.
	Command: python manage.py createsuperuser
   Alternatively you can use:
	Username: cs305oj
	Password: onlinejudge
2. Now ensure that the docker desktop in running on your local machine.
3. For running the project on local.
	Command: python manage.py runserver
4. For login go to http://127.0.0.1:8000/oj
5. Login with the superuser's credentials.
6. If you want to login as participant or setter either register first in the system or can use sample users already present in the system.
7. Go to http://127.0.0.1:8000/oj to test the participant's mode.(Admin is allowed to access participant's pages).
8. Go to http://127.0.0.1:8000/oj2 to test the setter's mode.(Admin is allowed to access setter's pages).
