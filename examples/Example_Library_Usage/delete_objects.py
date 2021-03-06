# =============================================================================
# Copyright [2014] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================

import os


HOME = os.getenv('HOME')


# Set some default args
import turbolift
args = turbolift.ARGS = {
    'os_user': 'YOURUSERNAME',    # Username
    'os_apikey': 'YOURAPIKEY',    # API-Key
    'os_rax_auth': 'YOURREGION',  # RAX Region, must be UPPERCASE
    'error_retry': 5,             # Number of failure retries
    'container': 'test9000',      # Name of the container
    'quiet': True,                # Make the application not print stdout
    'batch_size': 30000           # The number of jobs to do per cycle
}


# Load our Logger
from turbolift.logger import logger
log_method = logger.load_in(
    log_level='info',
    log_file='turbolift_library',
    log_location=HOME
)


# Load our constants
turbolift.load_constants(log_method, args)


# Authenticate against the swift API
from turbolift.authentication import authentication
authentication = authentication.authenticate()


# Package up the Payload
import turbolift.utils.http_utils as http
payload = http.prep_payload(
    auth=authentication,
    container=args.get('container'),
    source=args.get('source'),
    args=args
)


# Load all of our available cloud actions
from turbolift.clouderator import actions
cf_actions = actions.CloudActions(payload=payload)


# Delete file(s)
# =============================================================================
import turbolift.utils.multi_utils as multi

kwargs = {
    'url': payload['url'],              # Defines the Upload URL
    'container': payload['c_name']      # Sets the container
}

# Return a list of all objects that we will delete
objects, list_count, last_obj = cf_actions.object_lister(**kwargs)

# Get a list of all of the object names
object_names = [obj['name'] for obj in objects]

# Set the delete job
kwargs['cf_job'] = cf_actions.object_deleter

# Perform the upload job
multi.job_processer(
    num_jobs=list_count,
    objects=object_names,
    job_action=multi.doerator,
    concur=50,
    kwargs=kwargs
)
