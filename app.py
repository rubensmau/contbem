from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from supabase import create_client, Client
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Supabase Client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

@app.route("/")
def home():
    if 'user' in session:
        response = supabase.table("users").select("*").execute()
        is_admin = session.get('user') == 'rubensmau@gmail.com'
        return render_template("index.html", users=response.data, is_admin=is_admin)
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        response = supabase.table("users").select("*").eq("email", email).execute()
        if response.data:
            user = response.data[0]
            if check_password_hash(user["password"], password):
                session['user'] = user['email']
                session['user_name'] = user['name']
                return redirect(url_for('welcome'))
        flash("Credenciais inválidas")
        return redirect(url_for('login'))
    return render_template("login.html")

@app.route("/welcome")
def welcome():
    if 'user' in session:
        return render_template("welcome.html", user_email=session['user'])
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if 'user' not in session or session['user'] != 'rubensmau@gmail.com':
        flash("Você não está autorizado a acessar esta página.")
        return redirect(url_for('home'))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        response = supabase.table("users").select("*").eq("email", email).execute()
        if response.data:
            flash("Email já registrado")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = {"name": name, "email": email, "password": hashed_password}
        supabase.table("users").insert(new_user).execute()
        flash(f"Usuário {name} registrado com sucesso.")
        return redirect(url_for('home'))
    return render_template("register.html")

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        hashed_password = generate_password_hash(new_password)
        user_email = session['user']
        supabase.table("users").update({"password": hashed_password}).eq("email", user_email).execute()
        flash("Senha alterada com sucesso.")
        return redirect(url_for('welcome'))
    return render_template("change_password.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    flash("Você saiu com sucesso.")
    return redirect(url_for('login'))

# ============== ENTITIES ROUTES ==============
@app.route("/entities")
def entities():
    if 'user' not in session:
        return redirect(url_for('login'))
    response = supabase.table("entities").select("*").order("created_at", desc=True).execute()
    return render_template("entities.html", entities=response.data)

@app.route("/entities/new", methods=["GET", "POST"])
def new_entity():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        entity_data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "address": request.form.get("address"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "url": request.form.get("url")
        }
        supabase.table("entities").insert(entity_data).execute()
        flash("Entidade criada com sucesso.")
        return redirect(url_for('entities'))
    return render_template("entity_form.html", entity=None)

@app.route("/entities/<int:entity_id>/edit", methods=["GET", "POST"])
def edit_entity(entity_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        entity_data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "address": request.form.get("address"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "url": request.form.get("url")
        }
        supabase.table("entities").update(entity_data).eq("id", entity_id).execute()
        flash("Entidade atualizada com sucesso.")
        return redirect(url_for('entities'))

    response = supabase.table("entities").select("*").eq("id", entity_id).execute()
    return render_template("entity_form.html", entity=response.data[0] if response.data else None)

@app.route("/entities/<int:entity_id>/delete", methods=["POST"])
def delete_entity(entity_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    supabase.table("entities").delete().eq("id", entity_id).execute()
    flash("Entidade deletada com sucesso.")
    return redirect(url_for('entities'))

# ============== PERSONS ROUTES ==============
@app.route("/persons")
def persons():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Get filter parameters
    entity_id = request.args.get('entity_id', '')
    search = request.args.get('search', '')

    # Build query
    query = supabase.table("persons").select("*, entities(name)")

    # Apply entity filter
    if entity_id:
        query = query.eq("entity_id", entity_id)

    # Apply search filter (note: Supabase uses ilike for case-insensitive search)
    if search:
        query = query.ilike("name", f"%{search}%")

    response = query.order("created_at", desc=True).execute()

    # Get all entities for the filter dropdown
    entities_response = supabase.table("entities").select("*").order("name").execute()

    return render_template("persons.html", persons=response.data, entities=entities_response.data,
                         selected_entity=entity_id, search_query=search)

@app.route("/persons/new", methods=["GET", "POST"])
def new_person():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        person_data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "position": request.form.get("position"),
            "entity_id": request.form.get("entity_id")
        }
        supabase.table("persons").insert(person_data).execute()
        flash("Pessoa criada com sucesso.")
        return redirect(url_for('persons'))

    entities_response = supabase.table("entities").select("*").order("name").execute()
    return render_template("person_form.html", person=None, entities=entities_response.data)

@app.route("/persons/<int:person_id>/edit", methods=["GET", "POST"])
def edit_person(person_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        person_data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "position": request.form.get("position"),
            "entity_id": request.form.get("entity_id")
        }
        supabase.table("persons").update(person_data).eq("id", person_id).execute()
        flash("Pessoa atualizada com sucesso.")
        return redirect(url_for('persons'))

    person_response = supabase.table("persons").select("*").eq("id", person_id).execute()
    entities_response = supabase.table("entities").select("*").order("name").execute()
    return render_template("person_form.html", person=person_response.data[0] if person_response.data else None, entities=entities_response.data)

@app.route("/persons/<int:person_id>/delete", methods=["POST"])
def delete_person(person_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    supabase.table("persons").delete().eq("id", person_id).execute()
    flash("Pessoa deletada com sucesso.")
    return redirect(url_for('persons'))

# ============== EVENTS ROUTES ==============
@app.route("/events")
def events():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Get filter parameters
    entity_id = request.args.get('entity_id', '')
    search = request.args.get('search', '')

    # Build query
    query = supabase.table("events").select("*, entities(name), persons(name)")

    # Apply entity filter
    if entity_id:
        query = query.eq("entity_id", entity_id)

    # Apply search filter on entity name
    if search:
        # Note: We need to filter by entity name, but Supabase doesn't directly support filtering on joined tables
        # We'll fetch all and filter in Python as a workaround
        pass

    response = query.order("event_date", desc=True).execute()

    # If search is provided, filter by entity name in Python
    filtered_events = response.data
    if search:
        filtered_events = [event for event in response.data
                          if event.get('entities') and search.lower() in event['entities']['name'].lower()]

    # Get all entities for the filter dropdown
    entities_response = supabase.table("entities").select("*").order("name").execute()

    return render_template("events.html", events=filtered_events, entities=entities_response.data,
                         selected_entity=entity_id, search_query=search)

@app.route("/events/new", methods=["GET", "POST"])
def new_event():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        event_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "event_date": request.form.get("event_date"),
            "event_type": request.form.get("event_type"),
            "entity_id": request.form.get("entity_id"),
            "person_id": request.form.get("person_id") if request.form.get("person_id") else None
        }
        supabase.table("events").insert(event_data).execute()
        flash("Evento criado com sucesso.")
        return redirect(url_for('events'))

    entities_response = supabase.table("entities").select("*").order("name").execute()
    persons_response = supabase.table("persons").select("*").order("name").execute()
    return render_template("event_form.html", event=None, entities=entities_response.data, persons=persons_response.data)

@app.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        event_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "event_date": request.form.get("event_date"),
            "event_type": request.form.get("event_type"),
            "entity_id": request.form.get("entity_id"),
            "person_id": request.form.get("person_id") if request.form.get("person_id") else None
        }
        supabase.table("events").update(event_data).eq("id", event_id).execute()
        flash("Evento atualizado com sucesso.")
        return redirect(url_for('events'))

    event_response = supabase.table("events").select("*").eq("id", event_id).execute()
    entities_response = supabase.table("entities").select("*").order("name").execute()
    persons_response = supabase.table("persons").select("*").order("name").execute()
    return render_template("event_form.html", event=event_response.data[0] if event_response.data else None, entities=entities_response.data, persons=persons_response.data)

@app.route("/events/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    supabase.table("events").delete().eq("id", event_id).execute()
    flash("Evento deletado com sucesso.")
    return redirect(url_for('events'))

# ============== ACTIONS ROUTES ==============
@app.route("/actions")
def actions():
    if 'user' not in session:
        return redirect(url_for('login'))
    response = supabase.table("actions").select("*, entities(name)").order("due_date", desc=True).execute()
    return render_template("actions.html", actions=response.data)

@app.route("/actions/new", methods=["GET", "POST"])
def new_action():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        action_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "status": request.form.get("status"),
            "priority": request.form.get("priority"),
            "due_date": request.form.get("due_date") if request.form.get("due_date") else None,
            "entity_id": request.form.get("entity_id")
        }
        supabase.table("actions").insert(action_data).execute()
        flash("Ação criada com sucesso.")
        return redirect(url_for('actions'))

    entities_response = supabase.table("entities").select("*").order("name").execute()
    return render_template("action_form.html", action=None, entities=entities_response.data)

@app.route("/actions/<int:action_id>/edit", methods=["GET", "POST"])
def edit_action(action_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        action_data = {
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "status": request.form.get("status"),
            "priority": request.form.get("priority"),
            "due_date": request.form.get("due_date") if request.form.get("due_date") else None,
            "entity_id": request.form.get("entity_id")
        }
        supabase.table("actions").update(action_data).eq("id", action_id).execute()
        flash("Ação atualizada com sucesso.")
        return redirect(url_for('actions'))

    action_response = supabase.table("actions").select("*").eq("id", action_id).execute()
    entities_response = supabase.table("entities").select("*").order("name").execute()
    return render_template("action_form.html", action=action_response.data[0] if action_response.data else None, entities=entities_response.data)

@app.route("/actions/<int:action_id>/delete", methods=["POST"])
def delete_action(action_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    supabase.table("actions").delete().eq("id", action_id).execute()
    flash("Ação deletada com sucesso.")
    return redirect(url_for('actions'))

# ============== ENTITY DETAILS ==============
@app.route("/entities/<int:entity_id>/details")
def entity_details(entity_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    # Get entity details
    entity_response = supabase.table("entities").select("*").eq("id", entity_id).execute()
    if not entity_response.data:
        flash("Entidade não encontrada.")
        return redirect(url_for('entities'))

    # Get events for this entity
    events_response = supabase.table("events").select("*, persons(name)").eq("entity_id", entity_id).order("event_date", desc=True).execute()

    # Get actions for this entity
    actions_response = supabase.table("actions").select("*").eq("entity_id", entity_id).order("due_date", desc=True).execute()

    return render_template("entity_details.html",
                         entity=entity_response.data[0],
                         events=events_response.data,
                         actions=actions_response.data)

if __name__ == "__main__":
    app.run(debug=True)
