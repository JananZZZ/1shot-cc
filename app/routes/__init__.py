from flask import Blueprint


def register_blueprints(app):
    from app.routes.api_system import bp as system_bp
    from app.routes.api_install import bp as install_bp
    from app.routes.api_config import bp as config_bp
    from app.routes.api_tutorial import bp as tutorial_bp

    app.register_blueprint(system_bp)
    app.register_blueprint(install_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(tutorial_bp)

    # 前端页面路由
    from flask import render_template

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/wizard/<step>")
    def wizard(step):
        valid = [
            "check", "nodejs", "git", "claude",
            "ccswitch", "ccswitch_guide",
            "config", "final",
            "uninstall", "uninstall_done",
        ]
        if step not in valid:
            return render_template("index.html")
        return render_template(f"wizard_{step}.html")

    @app.route("/welcome")
    def welcome_page():
        return render_template("welcome.html")

    @app.route("/tutorial/<tutorial_id>")
    def tutorial_page(tutorial_id):
        mapping = {
            "claude": "tutorial_claude.html",
            "apikey": "tutorial_apikey.html",
            "ccswitch": "tutorial_ccswitch.html",
            "proxy": "tutorial_proxy.html",
        }
        tmpl = mapping.get(tutorial_id, "tutorial_claude.html")
        return render_template(tmpl)
