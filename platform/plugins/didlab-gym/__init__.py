from flask import Blueprint, render_template_string


def load(app):
    """
    Minimal DIDLab Gym plugin.

    Registers a /gym route that just shows a simple page.
    We'll expand this later to list challenges, courses, etc.
    """

    gym_bp = Blueprint(
        "didlab_gym",
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    @gym_bp.route("/gym")
    def gym_index():
        # Very simple placeholder page so we can confirm the plugin works.
        return render_template_string(
            """
            <!doctype html>
            <html lang="en">
            <head>
                <title>DIDLab Gym</title>
            </head>
            <body>
                <h1>DIDLab Gym</h1>
                <p>The DIDLab Gym plugin is loaded and working.</p>
                <p>We'll replace this with a challenge explorer once the base platform is stable.</p>
            </body>
            </html>
            """
        )

    # Register the blueprint with the main CTFd app
    app.register_blueprint(gym_bp)
