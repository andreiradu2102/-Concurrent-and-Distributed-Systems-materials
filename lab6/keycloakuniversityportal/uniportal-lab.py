import json
import os
import jwt
from jwt import PyJWKClient
import requests
from flask import Flask, redirect, request, session, url_for, render_template
from functools import wraps
from dotenv import load_dotenv

# ---------------- Load Configuration ----------------
# Do not change these (except for REDIRECT_URI, you can choose another port)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

# Environment variables
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
REALM = os.getenv("KEYCLOAK_REALM")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")

REDIRECT_URI = "http://localhost:8081/callback"

# Keycloak endpoints
AUTH_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/auth"
TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token"
LOGOUT_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/logout"
USERINFO_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/userinfo"
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

# ---------------- Helper Methods ----------------
# Do not change these

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            print(url_for("login"))
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(required_role):
    """Allow access if user has the required role OR is an admin."""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))
            roles = session["user"].get("realm_access", {}).get("roles", [])
            if "admin" in roles or required_role in roles:
                return f(*args, **kwargs)
            return render_template("access_denied.html")
        return decorated
    return wrapper

# ---------------- Routes ----------------

@app.route("/")
def home():
    if "user" in session:
        username = session["user"].get("preferred_username", "User")
        roles = session["user"].get("realm_access", {}).get("roles", [])
        role_info = ", ".join(roles) if roles else "No roles"

        return render_template("home.html", user=session["user"], username=username, role_info=role_info)
    return render_template("home.html", user=None)


@app.route("/login")
def login():
    auth_redirect = (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&response_type=code&scope=openid profile email"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_redirect)


@app.route("/callback")
def callback():
    # TODO: Extract the authorization code from the URL query parameters sent by Keycloak
    code = request.args.get("code")
    if not code:
        return render_template("login_failed.html", error="Missing authorization code")

    # TODO: Prepare the data for the token exchange request
    #   We should add grant type, authorization code, redirect URI (we already have it defined) and client id
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    # TODO: Make a POST request to Keycloak's token endpoint to exchange the authorization code for token
    try:
        resp = requests.post(TOKEN_URL, data=data, timeout=10)
    except requests.RequestException as e:
        return render_template("login_failed.html", error=f"Token request failed: {e}")
    
    if resp.status_code != 200:
        # Show Keycloak error if any
        try:
            err = resp.json()
        except Exception:
            err = {"error": f"HTTP {resp.status_code}", "body": resp.text[:300]}
        return render_template("login_failed.html", error=err)

    token_payload = resp.json()

    # TODO: Parse the token and extract: access token and identity token
    access_token = token_payload.get("access_token")
    id_token = token_payload.get("id_token")

    if not access_token:
        return render_template("login_failed.html", error="No access token in response")

    # TODO: Render "login_failed.html" template if no access token was found

    # Decode JWT
    try:
        jwks_client = PyJWKClient(JWKS_URL)
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        decoded_access = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False},  # ignore audience in this lab
        )
    except Exception as e:
        return render_template("login_failed.html", error=f"JWT verify/decode failed: {e}")

    # TODO: Store the decoded token, the access token and the identity token in the current session
    decoded_id = {}
    if id_token:
        try:
            id_signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            decoded_id = jwt.decode(
                id_token,
                id_signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        except Exception:
            # ignore silently; access token already decoded
            decoded_id = {}

    session["access_token"] = access_token
    session["id_token"] = id_token
    # prefer access token (has realm_access with roles); merge basic identity data if present
    user_claims = decoded_access.copy()
    for k in ("name", "given_name", "family_name", "preferred_username", "email"):
        if k not in user_claims and decoded_id.get(k):
            user_claims[k] = decoded_id[k]
    session["user"] = user_claims

    return redirect(url_for("home"))


@app.route("/student")
@login_required
@role_required("student")
def student_dashboard():
    username = session["user"].get("preferred_username")
    return render_template("student_dashboard.html", username=username)

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    username = session["user"].get("preferred_username")
    return render_template("admin_dashboard.html", username=username)

@app.route("/logout")
def logout():
    id_token = session.get("id_token")
    session.clear()

    logout_redirect = (
        f"{LOGOUT_URL}?client_id={CLIENT_ID}"
        f"&post_logout_redirect_uri={url_for('home', _external=True)}"
    )

    if id_token:
        logout_redirect += f"&id_token_hint={id_token}"

    return redirect(logout_redirect)

# Additional: Debug view to see decoded token content
@app.route("/debug")
def debug():
    import json
    user_data = json.dumps(session.get('user', {}), indent=2)
    return render_template("debug.html", user_data=user_data)


# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True, port=8081)
