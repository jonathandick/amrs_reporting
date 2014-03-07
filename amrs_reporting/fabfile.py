from fabric.api import local

def prepare_deployment(branch_name):
    # local('python manage.py test amrs_reporting')

    local('git add -p && git commit')
    

def deploy():
    with lcd('/var/www'):

        # With git...
        local('git pull /')



        # With both
        local('python manage.py migrate myapp')
        local('python manage.py test myapp')
        local('/my/command/to/restart/webserver')
