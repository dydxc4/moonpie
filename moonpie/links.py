from moonpie.db import get_db

def get_links():
  db = get_db()
  links = db.execute('SELECT id, title, url, icon FROM links').fetchall()
  return links
