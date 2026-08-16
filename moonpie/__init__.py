import os
from flask import Flask, jsonify, render_template
from . import links, monitor

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, 'moonpie.sqlite')
  )

  if test_config is None:
    app.config.from_pyfile('config.py', silent=True)
  else:
    app.config.from_mapping(test_config)

  os.makedirs(app.instance_path, exist_ok=True)

  @app.route('/api/system/info')
  def api_system_info():
    data = monitor.get_system_info()
    return jsonify(data)

  @app.route('/api/system/summary')
  def api_system_summary():
    summary = monitor.get_system_summary()
    return jsonify(summary)

  @app.route('/')
  def index():
    shortcuts = links.get_links()
    net_interfaces = monitor.get_network_interfaces()
    disks = monitor.get_disks()
    return render_template(
      'index.html',
      title='Dashboard',
      net_interfaces=net_interfaces,
      disks=disks,
      links=shortcuts,
    )

  from . import db
  db.init_app(app)

  return app
