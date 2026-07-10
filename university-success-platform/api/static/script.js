(() => {
    const FIELDS = [
      "n_assessments_submitted",
      "n_active_days",
      "total_clicks",
      "weighted_avg_score",
      "avg_score",
      "n_late_submissions",
    ];
  
    const tbody = document.getElementById("register-body");
    const rowTemplate = document.getElementById("row-template");
    const addRowBtn = document.getElementById("add-row-btn");
    const predictBtn = document.getElementById("predict-btn");
    const formError = document.getElementById("form-error");
    const ledDb = document.getElementById("led-db");
  
    // ---------- Row management ----------
    function reindexRows() {
      [...tbody.querySelectorAll(".register__row")].forEach((row, i) => {
        row.querySelector(".row-index").textContent = i + 1;
      });
    }
  
    function addRow() {
      const node = rowTemplate.content.firstElementChild.cloneNode(true);
      node.querySelector(".row-remove").addEventListener("click", () => {
        if (tbody.querySelectorAll(".register__row").length > 1) {
          node.remove();
          reindexRows();
        }
      });
      tbody.appendChild(node);
      reindexRows();
    }
  
    addRowBtn.addEventListener("click", addRow);
  
    // start with one row
    addRow();
  
    // ---------- Collect + validate ----------
    function collectStudents() {
      const rows = [...tbody.querySelectorAll(".register__row")];
      const students = [];
  
      for (const row of rows) {
        const student = {};
        for (const field of FIELDS) {
          const input = row.querySelector(`[data-field="${field}"]`);
          if (input.value === "" || !input.checkValidity()) {
            input.focus();
            throw new Error(
              `Vérifiez la valeur du champ « ${field.replaceAll("_", " ")} » (ligne ${
                rows.indexOf(row) + 1
              }).`
            );
          }
          student[field] = Number(input.value);
        }
        students.push(student);
      }
      return students;
    }
  
    function setVerdict(row, html, className) {
      const cell = row.querySelector(".verdict");
      cell.className = `verdict ${className}`;
      cell.innerHTML = html;
    }
  
    function renderVerdict(row, prediction) {
      // 1 / true / "pass" -> admis. 0 / false / "fail" -> risque. Otherwise show raw value.
      const normalized =
        typeof prediction === "boolean" ? (prediction ? 1 : 0) : prediction;
  
      if (normalized === 1 || normalized === "1") {
        setVerdict(row, "Admis", "verdict--stamp verdict--pass");
      } else if (normalized === 0 || normalized === "0") {
        setVerdict(row, "Risque d'échec", "verdict--stamp verdict--risk");
      } else {
        setVerdict(row, String(prediction), "verdict--raw");
      }
    }
  
    // ---------- Predict ----------
    predictBtn.addEventListener("click", async () => {
      formError.textContent = "";
      let students;
      try {
        students = collectStudents();
      } catch (err) {
        formError.textContent = err.message;
        return;
      }
  
      const rows = [...tbody.querySelectorAll(".register__row")];
      rows.forEach((row) => setVerdict(row, "…", "verdict--loading"));
  
      predictBtn.disabled = true;
      const originalLabel = predictBtn.textContent;
      predictBtn.textContent = "Prédiction en cours…";
  
      try {
        const res = await fetch("/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ students }),
        });
  
        const data = await res.json();
  
        if (!res.ok) {
          throw new Error(data.detail || "La prédiction a échoué.");
        }
  
        data.predictions.forEach((prediction, i) => {
          renderVerdict(rows[i], prediction);
        });
      } catch (err) {
        formError.textContent = err.message;
        rows.forEach((row) => setVerdict(row, "Erreur", "verdict--raw"));
      } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = originalLabel;
      }
    });
  
    // ---------- Live DB health LED ----------
    async function pollHealth() {
      try {
        const res = await fetch("/health");
        const data = await res.json();
        const ok = res.ok && data.database === "connected";
        ledDb.dataset.state = ok ? "ok" : "error";
        ledDb.querySelector(".led__label").textContent = ok
          ? "Base (DuckDB)"
          : "Base (DuckDB) — hors ligne";
      } catch {
        ledDb.dataset.state = "error";
        ledDb.querySelector(".led__label").textContent = "Base (DuckDB) — injoignable";
      }
    }
  
    pollHealth();
    setInterval(pollHealth, 15000);
  })();