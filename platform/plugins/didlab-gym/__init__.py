from flask import Blueprint, render_template
from CTFd.models import Challenges, Solves
from CTFd.utils.user import get_current_user


def load(app):
    """
    DIDLab Gym plugin.

    Provides a /gym page that lists all visible challenges as a
    course-agnostic practice view.
    """

    gym_bp = Blueprint(
        "didlab_gym",
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    @gym_bp.route("/gym")
    def gym_index():
        user = get_current_user()
        user_id = user.id if user else None

        # All *visible* challenges (no 'hidden' column in this CTFd version)
        challenges = (
            Challenges.query.filter(Challenges.state == "visible")
            .order_by(Challenges.category, Challenges.value, Challenges.name)
            .all()
        )

        # Challenges already solved by this user
        solved_ids = set()
        if user_id:
            solved_ids = {
                s.challenge_id
                for s in Solves.query.filter_by(user_id=user_id).all()
            }

        gym_chals = []
        for c in challenges:
            gym_chals.append(
                {
                    "id": c.id,
                    "name": c.name,
                    "category": c.category,
                    "value": c.value,
                    "solved": c.id in solved_ids,
                }
            )

        return render_template("gym_index.html", challenges=gym_chals)

    app.register_blueprint(gym_bp)
