async function refreshSummary() {
  const url = '/api/system/summary';
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`)
    }

    const data = await response.json();
    const localIp = document.getElementById('local-ip');
    const uptime = document.getElementById('uptime');
    const cpuTemperature = document.getElementById('cpu-temperature-navbar');

    localIp.textContent = data.local_ip;
    uptime.textContent = data.uptime;
    cpuTemperature.textContent = data.cpu_temperature;

  } catch (error) {
    console.error(error.message);
  }
}

function onLoad() {
  refreshSummary();
  setInterval(refreshSummary, 10000);
}

window.addEventListener('load', onLoad);
