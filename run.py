from config import DebugConfig
from adslabs import *
app = create_app(DebugConfig)
app.run(host='0.0.0.0')
