async function refreshData() {
  const url = '/api/system/info';
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`)
    }

    const data = await response.json();

    // Obtiene los elementos indicadores
    const cpuUsagePercent = document.getElementById('cpu-usage-percent');
    const coreUsagePercents = document.getElementById('core-usage-percents');
    const ramUsageTotals = document.getElementById('ram-usage-totals');
    const ramUsagePercent = document.getElementById('ram-usage-percent');
    const ramUsageProgressbar = document.getElementById('ram-usage-progressbar');
    const swapUsage = document.getElementById('swap-usage');
    const rxSpeed = document.getElementById('rx-speed');
    const txSpeed = document.getElementById('tx-speed');
    const cpuTemperature = document.getElementById('cpu-temperature');
    const cpuTemperatureProgressbar = document.getElementById('cpu-temperature-progressbar');

    // Porcentaje de uso de CPU
    cpuUsagePercent.innerText = toReadablePercent(data.cpu_usage.percent);
    // Porcentajes de uso por cada núcleo
    coreUsagePercents.innerHTML = '';
    data.cpu_usage.per_core_percents.forEach((percent, index) => {
      let node = document.createElement('span');
      node.innerText = `Core ${index}: ${toReadablePercent(percent)}`;
      coreUsagePercents.appendChild(node);
    });
    // Total/usado de RAM
    ramUsageTotals.innerText = `${data.ram_usage.total} / ${data.ram_usage.used}`;
    // Porcentaje de uso de RAM
    ramUsagePercent.innerText = toReadablePercent(data.ram_usage.percent);
    ramUsageProgressbar.classList.forEach((className, index) => {
      if (className.startsWith('w-')) {
        ramUsageProgressbar.classList.remove(className);
        return;
      }
    });
    ramUsageProgressbar.classList.add(`w-[${data.ram_usage.percent.toFixed(0)}%]`);
    // Uso de SWAP
    swapUsage.innerText = `Swap: ${data.swap_usage.used}`;
    // Velocidad de bajada
    rxSpeed.innerText = data.net_speeds.rx_speed;
    txSpeed.innerText = data.net_speeds.tx_speed;
    // Temperatura
    let progress = Math.max(Math.min(data.thermal.cpu, 80), 30);
    progress = (progress - 30) / 0.5;

    cpuTemperature.innerText = `${data.thermal.cpu} °C`;
    cpuTemperatureProgressbar.style.left = `${progress.toFixed(0)}%`;
  } catch (error) {
    console.error(error.message);
  }
}

function toReadablePercent(value) {
  return `${value.toFixed(1)} %`;
}

function onLoad() {
  refreshData();
  setInterval(refreshData, 10000);
}

window.addEventListener('load', onLoad);
