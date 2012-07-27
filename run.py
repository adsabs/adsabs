from config import DefaultConfig
from adslabs import *
app = create_app(DefaultConfig)
app.run()
