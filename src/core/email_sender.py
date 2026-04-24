import urllib.parse

def generate_mail_mailto(to_email, subject, body):
    """Génère un lien mailto pour ouvrir l'application mail par défaut."""
    subject_enc = urllib.parse.quote(subject)
    body_enc = urllib.parse.quote(body)
    return f"mailto:{to_email}?subject={subject_enc}&body={body_enc}"

def get_maps_link(city_name):
    """Génère un lien Google Maps pour la ville/lieu."""
    q = urllib.parse.quote(city_name)
    return f"https://www.google.com/maps/search/?api=1&query={q}"
