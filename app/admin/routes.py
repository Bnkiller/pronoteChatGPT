from flask import Blueprint, render_template, request, redirect, url_for
import mysql.connector

admin_bp = Blueprint('admin', __name__)

# Configuration de la connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",       # Remplace par ton utilisateur MySQL
    password="rootpassword",       # Remplace par ton mot de passe MySQL
    database="pronote1"   # Nom de la base de données
)

@admin_bp.route('/')
def admin_home():
    return render_template("home_admin.html")

@admin_bp.route('/sup')
def list_users():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")  # Sélection de tous les utilisateurs
    users = cursor.fetchall()
    cursor.close()
    return render_template("sup_user.html", users=users)

# Route pour afficher la page HTML des étudiants
@admin_bp.route('/students')
def students_page():
    cursor = db.cursor(dictionary=True)  # Récupération des résultats sous forme de dictionnaire
    cursor.execute("SELECT * FROM eleves")  
    eleves = cursor.fetchall()
    cursor.close()
    return render_template("students.html", eleves=eleves)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    cursor = db.cursor(dictionary=True)

    # Récupération des classes et matières avec noms explicites
    cursor.execute("SELECT id, classe FROM classes")
    classes = [(classe["id"], classe["classe"]) for classe in cursor.fetchall()]
    print(classes)

    cursor.execute("SELECT id, nom_matiere FROM matieres")
    matieres = [(matiere["id"], matiere["nom_matiere"]) for matiere in cursor.fetchall()]

    cursor.close()

    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (username, email, password, role))
        user_id = cursor.lastrowid

        if role == 'eleve':
            nom = request.form['nom']
            prenom = request.form['prenom']
            classe_id = request.form['classe_id']
            cursor.execute("INSERT INTO eleves (nom, prenom, classe_id) VALUES (%s, %s, %s)",
                           (nom, prenom, classe_id))
            eleve_id = cursor.lastrowid  # Récupérer l'ID de l'élève créé
            # Mettre à jour la table users avec l'ID de l'élève
            cursor.execute("UPDATE users SET ID_eleve = %s WHERE id = %s", (eleve_id, user_id))

        elif role == 'prof':
            nomp = request.form['nomp']
            matiere1 = request.form['matiere1']
            matiere2 = request.form['matiere2']
            matiere3 = request.form['matiere3']
            classe1 = request.form['classe1']
            classe2 = request.form['classe2']
            classe3 = request.form['classe3']
            print(request.form)  # Voir toutes les données envoyées par le formulaire

            cursor.execute("INSERT INTO prof (user_id, nom, matiere1, matiere2, matiere3, classe1, classe2, classe3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
               (user_id, nomp, matiere1, matiere2, matiere3, classe1, classe2, classe3))



        db.commit()
        cursor.close()
        return redirect(url_for('admin.add_user'))

    return render_template('add_user.html', classes=classes, matieres=matieres)
