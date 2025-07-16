# Framework
from ETS2LA.Utils import settings
from ETS2LA.Controls import *
from ETS2LA.Events import *
from ETS2LA.Plugin import *
from ETS2LA.UI import *
import time

class SettingsMenu(ETS2LAPage):
    # set a URL for your settings page
    url = "/settings/example_plugin"
    # this title will be the button text
    title = "Example Plugin"
    # and we want this page to show up in the settings
    location = ETS2LAPageLocation.SETTINGS

    # You need to handle the actions yourself.
    def handle_state_change(self, *args):
        if args: # If an arg is included the user clicked the checkbox
            value = args[0]
        else: # If it's not included the user clicked the container
            value = not settings.Get("ExamplePlugin", "state", True)
        settings.Set("ExamplePlugin", "state", value)
    
    def handle_interval_change(self, value):
        settings.Set("ExamplePlugin", "interval", value)
        
    def handle_hold_time_change(self, value):
        settings.Set("ExamplePlugin", "hold_time", value)

    def render(self):
        # This is a standard component for making your page
        # look like the rest
        TitleAndDescription(
            title="ExamplePlugin",
            description="This is an example plugin for the tutorial!"
        )
        
        # This is another premade component. You can see
        # all the different premade components and the raw items
        # they were made from in the definition.
        CheckboxWithTitleDescription(
            title="Send State",
            description="Send the state values to the UI to show a proggress bar.",
            # Default is the value currently shown
            default=settings.Get("ExamplePlugin", "state", True),
            # Changed is what gets called when something happens
            changed=self.handle_state_change
        )
        
        SliderWithTitleDescription(
            title="Interval",
            description="The interval time in seconds.",
            suffix=" seconds",
            # for sliders default is the value that is shown before the user
            # changes the value.
            default=settings.Get("ExamplePlugin", "interval", 1),
            min=1,
            max=10,
            step=1,
            changed=self.handle_interval_change,
        )

        SliderWithTitleDescription(
            title="Hold Time",
            description="The hold time in seconds.",
            suffix=" seconds",
            default=settings.Get("ExamplePlugin", "hold_time", 1),
            min=1,
            max=10,
            step=1,
            changed=self.handle_hold_time_change,
        )


# Create a control event to enable or disable the plugin
enable_disable = ControlEvent(
    alias="enable_disable_example_plugin",
    name="Toggle Example Plugin",
    type="button",
    description="Enable or disable the Example Plugin. When enabled will blink the highbeams.",
    default="n" # only works with keyboard keys
)

# The plugin class needs to be named Plugin!
class Plugin(ETS2LAPlugin):
    # You can hover over the PluginDescription in your code editor
    # to see all the available variables.
    description = PluginDescription(
        name="ExamplePlugin",
        version="1.0.0",
        description="An example plugin for ETS2LA.",
        modules=["SDKController"],
        fps_cap=20
    )
    
    interval = 3 # seconds
    hold_time = 3 # seconds
    enabled = False # default value for the plugin
    
    # Author should be an array of Author objects.
    # It's named author instead of authors for backwards
    # compatibility.
    author = [
        Author(
            name="Tumppi066",
            url="https://tumppi066.fi"
        )
    ]
    
    # Rember to explicitly add pages!
    pages = [SettingsMenu]

    # Controls have to be explicitly added as well!
    controls = [
        enable_disable
    ]
    
    # DO NOT USE __init__!
    # (if you absolutely must the remember to call super().__init__())
    
    # Use the init() function instead as that
    # is ran after the backend initialization.
    def init(self): 
        self.controller = self.modules.SDKController.SCSController()
        
    @events.on("enable_disable_example_plugin")
    def handle_event(self, value: bool):
        if value == False:
            return # button up event
        self.enabled = not self.enabled
        
    # The run() function will be called for each "frame".
    # REMEMBER: All functions in a class need the self argument!
    def run(self):
        if not self.enabled:
            return
        
        # You could also access the button value directly
        # enable_disable.pressed()
        
        hold_time = self.settings.hold_time
        interval_time = self.settings.interval
        use_state = self.settings.state
        
        # You need to manually handle the case where settings are
        # not yet initialized!
        if hold_time is None: 
            hold_time = self.hold_time
            self.settings.hold_time = hold_time
            
        if interval_time is None: 
            interval_time = self.interval
            self.settings.interval = interval_time
            
        if use_state is None: 
            use_state = True
            self.settings.state = use_state
        
        
        interval_end = time.time() + interval_time
        while time.time() < interval_end: # wait until the interval is over
            percentage = 1 - ((interval_end - time.time()) / interval_time)
            if use_state:
                self.state.text = "Waiting for lights..."
                self.state.progress = percentage
            time.sleep(0.1) # run at 10fps
            
        # And we can then use it according to the page
        self.controller.hblight = True
        time.sleep(1/20)
        self.controller.hblight = False

        hold_end = time.time() + hold_time
        while time.time() < hold_end: # wait until the hold time is over
            percentage = 1 - ((hold_end - time.time()) / hold_time)
            if use_state:
                self.state.text = "Holding lights..."
                self.state.progress = percentage
            time.sleep(0.1) # run at 10fps
        
        self.controller.hblight = True
        time.sleep(1/20)
        self.controller.hblight = False