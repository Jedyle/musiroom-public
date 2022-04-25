# Launch instructions

* Install requirements 

		pip install -r requirements.txt
		
* Create configuration

Go to musiroom/settings and create a file settings.py :

	from . import * # import __init__ configuration
	
	# override any config variable you need
	
	DATABASES = {
		'default': {
			'ENGINE': ...
			# add you postgresql configuration
		}
	}
	
* Init config variable

		export DJANGO_SETTINGS_MODULE=settings.settings

* Launch migrations and run

		cd musiroom
		./manage.py migrate
		./manage.py runserver
		
* Go to http://localhost:8000/api 

		
