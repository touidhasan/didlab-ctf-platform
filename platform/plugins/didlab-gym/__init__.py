from collections import defaultdict

from flask import Blueprint, render_template, redirect, request
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_user
from CTFd.models import (
    db,
    Challenges,
    Solves,
    Tags,
    Users,
    UserFields,
    UserFieldEntries,
)


def load(app):
    """
    DiDLAB CTF plugin.

    Routes:
    - /course-hub       : general landing page (your didlab_hub.html)
    - /gym              : course-aware practice view (filtered by course_code / section)
    - /gym/scoreboard   : course-aware scoreboard
    - before_request    : gently redirect / and /challenges to Gym / Hub
    """

    gym_bp = Blueprint(
        "didlab_gym",
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ---------------------------------------------------------
    # /course-hub : public landing page that uses didlab_hub.html
    # ---------------------------------------------------------
    @gym_bp.route("/course-hub")
    def course_hub():
        return render_template("didlab_hub.html")

    # ---------------------------------------------------------
    # Helper: read user custom fields
    # ---------------------------------------------------------
    def get_user_course_meta(user):
        course_code = None
        section = None
        term = None

        if user is None:
            return course_code, section, term

        entries = (
            db.session.query(UserFieldEntries, UserFields)
            .join(UserFields, UserFields.id == UserFieldEntries.field_id)
            .filter(UserFieldEntries.user_id == user.id)
            .all()
        )

        for entry, field in entries:
            name = (field.name or "").strip()
            value = (entry.value or "").strip()
            if name == "course_code":
                course_code = value
            elif name == "section":
                section = value
            elif name == "term":
                term = value

        return course_code, section, term

    # ---------------------------------------------------------
    # /gym : course-aware practice view
    # ---------------------------------------------------------
    @gym_bp.route("/gym")
    @authed_only
    def gym_index():
        user = get_current_user()
        course_code, section, term = get_user_course_meta(user)

        # Base query: only visible challenges
        if hasattr(Challenges, "state"):
            # CTFd 3.x
            query = Challenges.query.filter(Challenges.state != "hidden")
        else:
            # Older CTFd
            query = Challenges.query.filter_by(hidden=False)

        # Filter by course tag (e.g., COMP_SCI-361, COMP_SCI-381, etc.)
        if course_code:
            query = (
                query.join(Tags, Tags.challenge_id == Challenges.id)
                .filter(Tags.value == course_code)
            )

        challenges = query.order_by(Challenges.category, Challenges.value).all()

        # Which of these challenges has the current user solved?
        solved_ids = set()
        if user is not None:
            solved_rows = (
                Solves.query.filter_by(user_id=user.id)
                .with_entities(Solves.challenge_id)
                .all()
            )
            solved_ids = {row.challenge_id for row in solved_rows}

        # Group by category for display
        grouped = defaultdict(list)
        for chal in challenges:
            grouped[chal.category or "Uncategorized"].append(
                {
                    "id": chal.id,
                    "name": chal.name,
                    "points": chal.value,
                    "solved": chal.id in solved_ids,
                }
            )

        return render_template(
            "gym.html",
            grouped_challenges=grouped,
            course_code=course_code,
            section=section,
            term=term,
        )

    # ---------------------------------------------------------
    # /gym/scoreboard : course & section scoreboard
    # ---------------------------------------------------------
    @gym_bp.route("/gym/scoreboard")
    @authed_only
    def gym_scoreboard():
        user = get_current_user()
        course_code, section, term = get_user_course_meta(user)

        # Determine challenge IDs that belong to this course
        if hasattr(Challenges, "state"):
            base_chal_query = Challenges.query.filter(Challenges.state != "hidden")
        else:
            base_chal_query = Challenges.query.filter_by(hidden=False)

        if course_code:
            base_chal_query = base_chal_query.join(
                Tags, Tags.challenge_id == Challenges.id
            ).filter(Tags.value == course_code)

        course_chals = base_chal_query.with_entities(
            Challenges.id, Challenges.value
        ).all()

        chall_points = {cid: pts for cid, pts in course_chals}

        rows = []
        if chall_points:
            # All solves on these challenges
            solves = (
                Solves.query.filter(Solves.challenge_id.in_(chall_points.keys()))
                .with_entities(Solves.user_id, Solves.challenge_id)
                .all()
            )

            # Aggregate scores per user
            user_scores = defaultdict(int)
            seen = set()
            for uid, cid in solves:
                if (uid, cid) in seen:
                    continue
                seen.add((uid, cid))
                user_scores[uid] += chall_points.get(cid, 0)

            if user_scores:
                users = Users.query.filter(Users.id.in_(user_scores.keys())).all()
            else:
                users = []

            # Fetch their custom fields in bulk
            user_ids = [u.id for u in users]
            meta_map = defaultdict(dict)
            if user_ids:
                uf_entries = (
                    db.session.query(UserFieldEntries, UserFields)
                    .join(UserFields, UserFields.id == UserFieldEntries.field_id)
                    .filter(UserFieldEntries.user_id.in_(user_ids))
                    .all()
                )
                for entry, field in uf_entries:
                    fname = (field.name or "").strip()
                    val = (entry.value or "").strip()
                    meta_map[entry.user_id][fname] = val

            for u in users:
                meta = meta_map.get(u.id, {})
                u_course = meta.get("course_code", "")
                u_section = meta.get("section", "")
                u_term = meta.get("term", "")

                # Restrict the scoreboard to the same course & section as the current user
                if course_code and u_course != course_code:
                    continue
                if section and u_section != section:
                    continue

                rows.append(
                    {
                        "user_id": u.id,
                        "name": u.name or u.email,
                        "score": user_scores.get(u.id, 0),
                        "course_code": u_course,
                        "section": u_section,
                        "term": u_term,
                    }
                )

            # Rank by score descending
            rows.sort(key=lambda r: r["score"], reverse=True)
            rank = 1
            for r in rows:
                r["rank"] = rank
                rank += 1

        return render_template(
            "gym_scoreboard.html",
            rows=rows,
            course_code=course_code,
            section=section,
            term=term,
        )

    # Register blueprint
    app.register_blueprint(gym_bp)

    # ---------------------------------------------------------
    # before_request : adjust default navigation
    # ---------------------------------------------------------
    @app.before_request
    def didlab_default_routes():
        """
        1. Make /course-hub the main landing page for visitors.
        2. For logged-in students, / goes to /gym.
        3. /challenges is redirected to /gym unless the URL has ?from_gym=1.
        """
        if request.method != "GET":
            return

        path = request.path or "/"

        # Let admin, API, themes, and plugins behave normally
        if (
            path.startswith("/admin")
            or path.startswith("/api")
            or path.startswith("/themes")
            or path.startswith("/plugins")
        ):
            return

        # Root -> hub or gym
        if path == "/":
            user = get_current_user()
            if user is not None:
                return redirect("/gym")
            return redirect("/course-hub")

        # /challenges -> /gym, unless explicitly coming from gym
        if path == "/challenges":
            if request.args.get("from_gym") == "1":
                # Already coming from Gym; let CTFd handle it
                return
            user = get_current_user()
            if user is not None:
                return redirect("/gym")
            # Anonymous: let CTFd redirect to /login normally
            return
