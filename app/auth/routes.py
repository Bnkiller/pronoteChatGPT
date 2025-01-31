from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import db, User
from app.auth.forms import LoginForm
from app.auth import auth_bp  # ✅ Importation correcte

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # Vérification en clair
            login_user(user)


            # 📌 Enregistrement de l'ID de l'utilisateur dans la session
            session['user_id'] = user.id  # Stocke l'ID utilisateur dans la session
            print("Session après connexion:", session)


            # 📌 Correction : Vérifie que l'utilisateur a bien un rôle
            if user.role == "admin":
                return redirect(url_for("admin.admin_home"))
            elif user.role == "prof":
                return redirect(url_for("prof.home_page_prof"))
            elif user.role == "eleve":
                return redirect(url_for("eleve.eleve_home"))
            else:
                flash("Rôle utilisateur inconnu", "warning")
                return redirect(url_for("auth.login"))

        flash("Identifiants invalides", "danger")

    return render_template('login.html', form=form)
