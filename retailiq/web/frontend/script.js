
const API = "http://127.0.0.1:8000/api";
let salesChart, categoryChart, forecastChart;

async function getData(endpoint) {
  const r = await fetch(`${API}/${endpoint}`);
  if (!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}

function fmt(n) {
  return Number(n || 0).toLocaleString("en-US", {maximumFractionDigits: 2});
}

function makeTable(id, rows) {
  const table = document.getElementById(id);
  if (!rows?.length) {
    table.innerHTML = "<tr><td>No records</td></tr>";
    return;
  }
  const cols = Object.keys(rows[0]);
  table.innerHTML = `
    <thead><tr>${cols.map(c => `<th>${c}</th>`).join("")}</tr></thead>
    <tbody>${rows.map(row => `<tr>${cols.map(c =>
      `<td>${row[c] ?? ""}</td>`).join("")}</tr>`).join("")}</tbody>`;
}

function downloadTable(id, filename) {
  const table = document.getElementById(id);
  const csv = [...table.rows].map(row =>
    [...row.cells].map(cell => `"${cell.innerText.replaceAll('"','""')}"`).join(",")
  ).join("\n");
  const blob = new Blob([csv], {type:"text/csv"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function chart(id, type, labels, datasets, old) {
  if (old) old.destroy();
  return new Chart(document.getElementById(id), {
    type, data:{labels,datasets},
    options:{
      responsive:true,
      plugins:{legend:{labels:{color:"#b9c7df"}}},
      scales:{
        x:{ticks:{color:"#8799b8"},grid:{color:"#24314b"}},
        y:{ticks:{color:"#8799b8"},grid:{color:"#24314b"}}
      }
    }
  });
}

async function loadAll() {
  try {
    const [s,p,i,d] = await Promise.all([
      getData("summary"), getData("predictions"),
      getData("inventory"), getData("data")
    ]);

    document.getElementById("apiStatus").textContent = "Connected";
    document.getElementById("mae").textContent = fmt(s.mae);
    document.getElementById("rmse").textContent = fmt(s.rmse);
    document.getElementById("wape").textContent = fmt(s.wape) + "%";
    document.getElementById("units").textContent = fmt(s.order_units);
    document.getElementById("cost").textContent = fmt(s.purchase_cost);
    document.getElementById("unmet").textContent = fmt(s.unmet_demand);

    salesChart = chart("salesChart","line",
      s.trend.map(x=>x.date),
      [{label:"Sales",data:s.trend.map(x=>x.sales),borderColor:"#6c8cff",tension:.3}],
      salesChart);

    categoryChart = chart("categoryChart","bar",
      s.categories.map(x=>x.family),
      [{label:"Units",data:s.categories.map(x=>x.units),backgroundColor:"#39d9a4"}],
      categoryChart);

    const predictions = p.rows || [];
    makeTable("predTable",predictions);
    forecastChart = chart("forecastChart","line",
      predictions.map(x=>x.date),
      [
        {label:"Actual",data:predictions.map(x=>x.actual ?? x.sales),borderColor:"#39d9a4"},
        {label:"Predicted",data:predictions.map(x=>x.prediction),borderColor:"#6c8cff"}
      ],forecastChart);

    makeTable("invTable",i.rows);
    makeTable("dataTable",d.rows);

  } catch(e) {
    document.getElementById("apiStatus").textContent = "Disconnected";
    console.error(e);
  }
}

document.querySelectorAll(".nav").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll(".nav").forEach(b=>b.classList.remove("active"));
    document.querySelectorAll(".page").forEach(p=>p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.page).classList.add("active");
    document.getElementById("pageTitle").textContent = btn.textContent.trim();
  };
});

loadAll();
