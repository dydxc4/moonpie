from flask import Flask, jsonify, render_template, redirect
from monitor import get_disks, get_network_interfaces, get_system_info

app = Flask(__name__)

@app.route('/api/system/info')
def api_sustem_info():
  data = get_system_info()
  return jsonify(data)

@app.route('/')
def index():
  net_interfaces = get_network_interfaces()
  disks = get_disks()
  return render_template('index.html', net_interfaces=net_interfaces, disks=disks)
