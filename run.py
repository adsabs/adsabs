from config import DefaultConfig
from adslabs import *
app = create_app(DefaultConfig)
app.run(host='0.0.0.0')
