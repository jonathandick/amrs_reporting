from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://github.com/jonathandick/amrs_reporting'

def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host) 
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run('mkdir -p %s/%s' % (site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, source_folder)) 
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


# NOT UPDATED; taken from http://chimera.labs.oreilly.com/books/1234000000754/ch09.html#_breakdown_of_a_fabric_script_for_our_deployment
def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/conf/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")  #1
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["%s"]' % (site_name,)  #2
    )
    secret_key_file = source_folder + '/superlists/secret_key.py'
    if not exists(secret_key_file):  #3
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


# NOT UPDATED; taken from http://chimera.labs.oreilly.com/books/1234000000754/ch09.html#_breakdown_of_a_fabric_script_for_our_deployment
def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'): 
        run('virtualenv --python=python3 %s' % (virtualenv_folder,))
    run('%s/bin/pip install -r %s/requirements.txt' % ( #2
            virtualenv_folder, source_folder
    ))




def prepare_deployment(branch_name):
    # local('python manage.py test amrs_reporting')
    local('git add -p && git commit')

APPS = ('report','ltfu','report_table','amrs_user_validation')

def deploy():
    with lcd('/var/www'):

        # With git...
        local('git pull ')
        # With both
        for app in APPS :
            local('python manage.py migrate ' + app)
            #local('python manage.py test myapp')

        local('python manage.py collectstatic')            
        local('sudo service apache2 restart')
