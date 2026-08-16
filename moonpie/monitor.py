import psutil
import socket
import time
from datetime import datetime, timedelta

# Variable global para registrar bytes previos y calcular velocidad
_prev_net_io = psutil.net_io_counters()
_prev_time = time.time()

def format_size(value):
  if value >= 1024 ** 4:
    return f'{round(value / 1024 ** 4, 1)} TB'
  elif value >= 1024 ** 3:
    return f'{round(value / 1024 ** 3, 1)} GB'
  elif value >= 1024 ** 2:
    return f'{round(value / 1024 ** 2, 1)} MB'
  elif value >= 1024:
    return f'{value / 1024} kB'
  else:
    return f'{value} bytes'

def format_bitrate(value):
  return f'{round(value, 0)} Mbps'

def format_timedelta(value: timedelta):
  result = ''
  seconds = value.seconds
  hours = int(seconds / 3600)
  seconds %= 3600

  if value.days > 0:
    result = f'{value.days}d '

  if hours > 0:
    result += f'{hours}h '

  minutes = int(seconds / 60)
  seconds %= 60

  if minutes > 0:
    result += f'{minutes}m '

  if seconds > 0:
    result += f'{seconds}s'

  return result.lstrip()

def get_partition_usage(mountpoint: str):
  usage = psutil.disk_usage(mountpoint)
  return {
    'total': format_size(usage.total),
    'used': format_size(usage.used),
    'percent': usage.percent
  }

def get_disks():
  return [{
      'device': partition.device,
      'mount_point': partition.mountpoint,
      'usage': get_partition_usage(partition.mountpoint)
    } for partition in psutil.disk_partitions()
  ]

def get_network_interfaces():
  addrs = psutil.net_if_addrs()
  stats = psutil.net_if_stats()
  interfaces_data = []

  for iface_name, iface_addrs in addrs.items():
    # Omitir interfaz local (loopback) para optimizar espacio en pantalla
    if iface_name == 'lo':
      continue

    is_up = stats[iface_name].isup if iface_name in stats else False
    mac = "N/A"
    ipv4 = "N/A"
    ipv6 = "N/A"

    for addr in iface_addrs:
      # Identificar familias de direcciones
      if addr.family == psutil.AF_LINK:
        mac = addr.address
      elif addr.family == socket.AF_INET:
        ipv4 = addr.address
      elif addr.family == socket.AF_INET6:
        # Tomar solo la primera parte de IPv6 si es muy larga
        ipv6 = addr.address.split('%')[0]

    interfaces_data.append({
      "name": iface_name,
      "status": "UP" if is_up else "DOWN",
      "mac": mac,
      "ipv4": ipv4,
      "ipv6": ipv6
    })

  return interfaces_data

def get_network_speeds():
  global _prev_net_io, _prev_time

  current_time = time.time()
  current_net_io = psutil.net_io_counters()

  time_delta = current_time - _prev_time
  if time_delta <= 0:
    time_delta = 1.0 # Evitar división por cero

  # Calcular diferencia de bytes y convertir a Kilobytes por segundo (KB/s)
  bytes_recv = current_net_io.bytes_recv - _prev_net_io.bytes_recv
  bytes_sent = current_net_io.bytes_sent - _prev_net_io.bytes_sent

  rx_speed = (bytes_recv / 1024) / time_delta
  tx_speed = (bytes_sent / 1024) / time_delta

  # Actualizar lecturas previas
  _prev_net_io = current_net_io
  _prev_time = current_time

  return {
    'rx_speed': format_bitrate(rx_speed),
    'tx_speed': format_bitrate(tx_speed)
  }

def get_cpu_temperature():
  temperatures = psutil.sensors_temperatures()
  value = 0

  if 'cpu_thermal' in temperatures:
    value = temperatures['cpu_thermal'][0].current
  elif 'coretemp' in temperatures:
    value = temperatures['coretemp'][0].current

  return round(value, 1)

def get_system_info():
  mem_usage = psutil.virtual_memory()
  swap_usage = psutil.swap_memory()
  net_speeds = get_network_speeds()

  data = {
    'cpu_usage': {
      'percent': psutil.cpu_percent(interval=0.5),
      'per_core_percents': psutil.cpu_percent(percpu=True, interval=0.5),
      'count': psutil.cpu_count()
    },
    'ram_usage': {
      'used': format_size(mem_usage.used),
      'total': format_size(mem_usage.total),
      'percent': mem_usage.percent,
    },
    'swap_usage': {
      'used': format_size(swap_usage.used),
      'total': format_size(swap_usage.total),
      'percent': swap_usage.percent,
    },
    'net_speeds': net_speeds,
    'thermal': {
      'cpu': get_cpu_temperature()
    }
  }

  return data

def get_system_summary():
  addrs = psutil.net_if_addrs()
  stats = psutil.net_if_stats()
  ipv4 = 'UNKNOWN'
  boot_time = datetime.fromtimestamp(psutil.boot_time())
  delta = datetime.now() - boot_time

  for iface_name, iface_addrs in addrs.items():
    is_up = stats[iface_name].isup if iface_name in stats else False

    if iface_name == 'lo' or not is_up:
      continue

    for addr in iface_addrs:
      if addr.family == socket.AF_INET:
        ipv4 = addr.address
        break

  data = {
    'cpu_temperature': get_cpu_temperature(),
    'local_ip': ipv4,
    'uptime': format_timedelta(delta)
  }

  return data
