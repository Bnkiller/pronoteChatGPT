from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify
import mysql.connector

eleve_bp = Blueprint('eleve', __name__)

# Configuration de la connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    database="pronote1"
)

# Données statiques pour l'emploi du temps élève
emploi_du_temps_ele = [
    {"jour": "Lundi", "heure": "08:00 - 10:00", "activité": "Mathématiques"},
    {"jour": "Lundi", "heure": "10:00 - 12:00", "activité": "Histoire"},
    {"jour": "Mardi", "heure": "09:00 - 11:00", "activité": "Physique"},
]

@eleve_bp.route('/')
def eleve_home():
    return render_template("home_ele.html")

# Route pour afficher l'emploi du temps élève
@eleve_bp.route("/edt")
def emploi_du_temps_page_ele():
    return render_template("edt_ele.html", emploi=emploi_du_temps_ele)

# Route pour afficher les notes d'un élève connecté
@eleve_bp.route("/notes")
def notes_eleve():
    if "user_id" not in session:  # Vérifie si l'utilisateur est connecté
        flash("Veuillez vous connecter.", "danger")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]  # Récupération de l'ID utilisateur

    cursor = db.cursor(dictionary=True)

    # Récupération de l'ID de l'élève
    query_id_eleve = "SELECT ID_eleve FROM users WHERE id = %s"
    cursor.execute(query_id_eleve, (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        flash("Utilisateur non trouvé.", "danger")
        return redirect(url_for("auth.login"))

    id_eleve = result["ID_eleve"]

    # Récupérer les notes
    query_notes = """
    SELECT m.nom_matiere, n.note, n.coef
    FROM notes n
    JOIN matieres m ON n.matiere_id = m.id
    WHERE n.eleve_id = %s
    ORDER BY m.nom_matiere;
    """
    cursor.execute(query_notes, (id_eleve,))
    notes = cursor.fetchall()

    # Calcul de la moyenne par matière
    query_moyennes = """
    SELECT m.nom_matiere, 
    SUM(n.note * n.coef) / SUM(n.coef) AS moyenne
    FROM notes n
    JOIN matieres m ON n.matiere_id = m.id
    WHERE n.eleve_id = %s
    GROUP BY m.nom_matiere;
    """
    cursor.execute(query_moyennes, (id_eleve,))
    moyennes = cursor.fetchall()

    # Calcul de la moyenne globale
    query_moyenne_globale = """
    SELECT AVG(moyenne) AS moyenne_globale
    FROM (
        SELECT SUM(n.note * n.coef) / SUM(n.coef) AS moyenne
        FROM notes n
        JOIN matieres m ON n.matiere_id = m.id
        WHERE n.eleve_id = %s
        GROUP BY m.nom_matiere
    ) AS sous_requete;
    """
    cursor.execute(query_moyenne_globale, (id_eleve,))
    moyenne_globale_result = cursor.fetchone()
    moyenne_globale = moyenne_globale_result["moyenne_globale"] if moyenne_globale_result and moyenne_globale_result["moyenne_globale"] is not None else 0

    cursor.close()

    return render_template("notes_eleve.html", notes=notes, moyennes=moyennes, moyenne_globale=moyenne_globale)

# Route pour afficher les absences d'un élève connecté
@eleve_bp.route("/absences")
def absences_eleve():
    if "user_id" not in session:  # Vérifier si l'élève est connecté
        flash("Veuillez vous connecter.", "danger")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]  # Récupération de l'ID utilisateur

    cursor = db.cursor(dictionary=True)

    # Récupération de l'ID de l'élève
    query_id_eleve = "SELECT ID_eleve FROM users WHERE id = %s"
    cursor.execute(query_id_eleve, (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        flash("Utilisateur non trouvé.", "danger")
        return redirect(url_for("auth.login"))

    id_eleve = result["ID_eleve"]

    # Récupération des absences
    query_absences = """
    SELECT a.heure_absence, m.nom_matiere, p.nom AS prof_nom
    FROM absences a
    JOIN matieres m ON a.id_matiere = m.id
    JOIN prof p ON a.id_prof = p.id
    WHERE a.id_eleve = %s
    ORDER BY a.heure_absence DESC;
    """
    cursor.execute(query_absences, (id_eleve,))
    absences = cursor.fetchall()

    cursor.close()

    return render_template("abs.html", absences=absences)

