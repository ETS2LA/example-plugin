# Framework
from ETS2LA.Events import *
from ETS2LA.Plugin import *

class Plugin(ETS2LAPlugin):
    description = PluginDescription(
        name="Example",
        version="1.0",
        description="This is an example plugin.",
        modules=["TruckSimAPI"],
        listen=["*.py"],
        fps_cap=2
    )
    
    author = Author(
        name="Tumppi066",
        url="https://github.com/Tumppi066",
        icon="https://avatars.githubusercontent.com/u/83072683?v=4"
    )

    def init(self):
        ...

    def run(self):
        ...