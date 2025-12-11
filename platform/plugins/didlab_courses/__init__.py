# platform/plugins/didlab-courses/__init__.py

from CTFd.plugins import (
    register_plugin_assets_directory,
    register_plugin_script,
)

def load(app):
    # Serve static assets for this plugin
    register_plugin_assets_directory(app, base_path="/plugins/didlab-courses/assets")

    # Inject our registration dropdown script
    register_plugin_script("/plugins/didlab-courses/assets/didlab_registration.js")
