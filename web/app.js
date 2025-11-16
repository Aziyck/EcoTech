document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("bonitareForm");
    const container = document.getElementById("formContaner");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();   // NU trimite pagina

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        console.log("DATE TRIMISE:", data);

        // Trimitem către Python
        const result = await eel.calc_note_de_bonitare_dict(data)();
        const arr = Object.entries(result).map(([key, value]) => ({
            name: key,
            ...value
        }));

        // Sortăm descrescător după general
        arr.sort((a, b) => b.general - a.general);
        console.log("RĂSPUNS SORTAT:", arr);

        // POPULARE PODIUM
        if (arr[0]) {
            document.getElementById("name1").textContent = arr[0].name;
            document.getElementById("score1").textContent = arr[0].general;
        }
        if (arr[1]) {
            document.getElementById("name2").textContent = arr[1].name;
            document.getElementById("score2").textContent = arr[1].general;
        }
        if (arr[2]) {
            document.getElementById("name3").textContent = arr[2].name;
            document.getElementById("score3").textContent = arr[2].general;
        }

        // POPULARE TABEL CU DETALII ACORDEON
        const tbody = document.getElementById("resultsTableBody");
        tbody.innerHTML = ""; // golim tabelul

        arr.forEach((item, index) => {
            // rând principal
            const tr = document.createElement("tr");
            tr.classList.add("table-row-clickable");
            tr.setAttribute("data-bs-toggle", "collapse");
            tr.setAttribute("data-bs-target", `#detail-${index}`);
            tr.setAttribute("aria-expanded", "false");
            tr.setAttribute("aria-controls", `detail-${index}`);
            tr.style.cursor = "pointer";

            // adăugăm iconița în ultimul td
            tr.innerHTML = `
        <td>${index + 1}</td>
        <td>${item.name}</td>
        <td>
            ${item.general}
            <span class="accordion-icon float-end">&#8250;</span>
        </td>
    `;
            tbody.appendChild(tr);

            // rând detalii (collapse)
            const detailTr = document.createElement("tr");
            detailTr.classList.add("detail-row");
            const detailTd = document.createElement("td");
            detailTd.colSpan = 3;

            const collapseDiv = document.createElement("div");
            collapseDiv.classList.add("collapse");
            collapseDiv.id = `detail-${index}`;
            collapseDiv.style.textAlign = "left";
            collapseDiv.style.backgroundColor = "#f1fdf3";

            let coefHTML = '';
            const entries = Object.entries(item).filter(([key]) => key !== 'name' && key !== 'general');

            entries.forEach(([key, value], i) => {
                let style = 'padding-left: 0.7rem;';
                if (i == 0) style += 'padding-top: 0.7rem;';
                if (i == entries.length - 1) style += 'padding-bottom: 0.7rem;';
                coefHTML += `<div style="${style}"><strong>${key}:</strong> ${value}</div>`;
            });
            collapseDiv.innerHTML = coefHTML;

            detailTd.appendChild(collapseDiv);
            detailTr.appendChild(detailTd);
            tbody.appendChild(detailTr);

            // ROTIRE ICONIȚĂ la deschidere
            collapseDiv.addEventListener('show.bs.collapse', () => {
                tr.querySelector('.accordion-icon').style.transform = 'rotate(90deg)';
            });
            collapseDiv.addEventListener('hide.bs.collapse', () => {
                tr.querySelector('.accordion-icon').style.transform = 'rotate(0deg)';
            });
        });


        // ARĂTĂ CONTAINER REZULTATE
        document.getElementById("resultsContainer").style.display = "block";
        // ASCUNDE FORMULAR
        form.style.display = "none";
        container.style.display = "none";
    });

    const backBtn = document.getElementById("backToCalc");

    backBtn.addEventListener("click", () => {
        document.getElementById("resultsContainer").style.display = "none";
        document.getElementById("bonitareForm").style.display = "block";
        document.getElementById("formContaner").style.display = "block";

        // Reset podium (opțional)
        document.getElementById("name1").textContent = "";
        document.getElementById("score1").textContent = "0.0";
        document.getElementById("name2").textContent = "";
        document.getElementById("score2").textContent = "0.0";
        document.getElementById("name3").textContent = "";
        document.getElementById("score3").textContent = "0.0";

        // Golim tabelul (opțional)
        document.getElementById("resultsTableBody").innerHTML = "";
    });



});



