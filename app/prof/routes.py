from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import datetime
from app.prof.forms import NoteForm  # Import du formulaire

prof_bp = Blueprint('prof', __name__)

# Configuration de la connexion MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    database="pronote1"
)

# Données statiques pour l'emploi du temps prof
emploi_du_temps_prof = [
    {"jour": "Jeudi", "heure": "08:00 - 10:00", "activité": "Mathématiques"},
    {"jour": "Jeudi", "heure": "10:00 - 12:00", "activité": "Histoire"},
    {"jour": "Dimanche", "heure": "09:00 - 11:00", "activité": "Physique"},
]

@prof_bp.route('/')
def home_page_prof():
    return render_template("home_prof.html")

# Route pour afficher les notes et ajouter une nouvelle note
@prof_bp.route("/notes", methods=["GET", "POST"])
def notes_prof():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT id FROM prof WHERE user_id = %s", (session.get("user_id"),))
    prof_data = cursor.fetchone()
    prof_id = prof_data["id"] if prof_data else None

    if not prof_id:
        flash("Accès refusé.", "danger")
        return redirect(url_for("auth.login"))

    # Récupérer les classes et matières enseignées par le prof
    cursor.execute("SELECT classe1, classe2, classe3, matiere1, matiere2, matiere3 FROM prof WHERE id = %s", (prof_id,))
    prof_data = cursor.fetchone()

    if not prof_data:
        flash("Erreur : Professeur introuvable.", "danger")
        return redirect(url_for("auth.login"))

    classes_autorisees = [prof_data[key] for key in ['classe1', 'classe2', 'classe3'] if prof_data.get(key)]
    matieres_autorisees = [prof_data[key] for key in ['matiere1', 'matiere2', 'matiere3'] if prof_data.get(key)]

    if not classes_autorisees:
        flash("Vous n'avez pas de classe attribuée.", "warning")
        return redirect(url_for("prof.home_page_prof"))

    # Ajout des classes où le prof enseigne dans le formulaire de filtrage
    cursor.execute(f"SELECT id, classe FROM classes WHERE id IN ({', '.join(['%s'] * len(classes_autorisees))})", tuple(classes_autorisees))
    classes_enseignees = cursor.fetchall()
    form = NoteForm()
    form.classe_id.choices = [(classe["id"], classe["classe"]) for classe in classes_enseignees]

    # Gestion du filtre par classe
    classe_id_filtre = request.args.get("classe_id")
    if classe_id_filtre and classe_id_filtre.isdigit():
        classe_id_filtre = int(classe_id_filtre)
    else:
        classe_id_filtre = None

    # Récupérer les élèves en fonction de la classe sélectionnée
    if classe_id_filtre:
        cursor.execute("SELECT id, nom, prenom FROM eleves WHERE classe_id = %s", (classe_id_filtre,))
    else:
        cursor.execute("SELECT id, nom, prenom FROM eleves")

    eleves = cursor.fetchall()
    form.eleve_id.choices = [(eleve["id"], f"{eleve['nom']} {eleve['prenom']}") for eleve in eleves]

    # Récupérer les matières disponibles
    cursor.execute("SELECT id, nom_matiere FROM matieres")
    matieres = cursor.fetchall()
    form.matiere_id.choices = [(matiere["id"], matiere["nom_matiere"]) for matiere in matieres]

    # Récupérer les notes selon la classe filtrée
    if classe_id_filtre:
        cursor.execute("""
            SELECT n.id AS note_id, e.nom, e.prenom, m.nom_matiere, n.coef, n.note
            FROM notes n
            JOIN eleves e ON n.eleve_id = e.id
            JOIN matieres m ON n.matiere_id = m.id
            WHERE e.classe_id = %s
            ORDER BY e.nom, m.nom_matiere
        """, (classe_id_filtre,))
    else:
        cursor.execute("""
            SELECT n.id AS note_id, e.nom, e.prenom, m.nom_matiere, n.coef, n.note
            FROM notes n
            JOIN eleves e ON n.eleve_id = e.id
            JOIN matieres m ON n.matiere_id = m.id
            ORDER BY e.nom, m.nom_matiere
        """)

    notes = cursor.fetchall()

    if form.validate_on_submit():
        eleve_id = form.eleve_id.data
        matiere_id = form.matiere_id.data
        note = form.note.data
        coef = form.coef.data

        cursor.execute("INSERT INTO notes (eleve_id, matiere_id, note, coef) VALUES (%s, %s, %s, %s)",
                       (eleve_id, matiere_id, note, coef))
        db.commit()
        flash("Note ajoutée avec succès !", "success")
        return redirect(url_for("prof.notes_prof"))

    cursor.close()
    return render_template("notes_prof.html", notes=notes, form=form)

# Route pour enregistrer l'appel et stocker les absences
@prof_bp.route('/enregistrer_appel', methods=['POST'])
def enregistrer_appel():
    cursor = db.cursor(dictionary=True)

    absents = request.form.getlist('absents')
    id_prof = session.get("user_id")
    id_matiere = request.form.get("id_matiere")

    if not id_prof:
        flash("Erreur : Professeur non identifié.", "danger")
        return redirect(url_for("prof.appel"))

    if not absents or not id_matiere:
        flash("Aucun élève sélectionné ou matière non définie.", "warning")
        return redirect(url_for("prof.appel"))

    for id_eleve in absents:
        cursor.execute(
            "INSERT INTO absences (id_eleve, id_prof, id_matiere, heure_absence) VALUES (%s, %s, %s, %s)",
            (id_eleve, id_prof, id_matiere, datetime.now())
        )

    db.commit()
    cursor.close()

    flash("Appel enregistré avec succès !", "success")
    return redirect(url_for("prof.appel"))

# Route pour supprimer une note
@prof_bp.route("/notes/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    db.commit()
    cursor.close()
    flash("Note supprimée avec succès !", "success")
    return redirect(url_for("prof.notes_prof"))

# Route pour afficher l'emploi du temps prof
@prof_bp.route("/appel")
def appel():
    return render_template("appel.html")

@prof_bp.route("/edt")
def emploi_du_temps_page_prof():
    return render_template("edt_prof.html", emploi=emploi_du_temps_prof)
