import os
from flask import current_app

SIGNATURES_ROOT = os.path.join(current_app.instance_path, 'media', 'signatures')
