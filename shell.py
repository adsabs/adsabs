# -*- coding: utf-8 -*-

import os

from flask.ext.script import Manager, prompt, prompt_pass, prompt_bool #@UnresolvedImport

from adsabs import create_app
from config import DebugConfig

manager = Manager(create_app())

from adsabs import create_app
app = create_app(DebugConfig)
project_root_path = os.path.join(os.path.dirname(app.root_path))


@manager.command
def run():
    """Run server that can be reached from anywhere."""
    app.run(host='0.0.0.0')


if __name__ == "__main__":
    manager.run()
