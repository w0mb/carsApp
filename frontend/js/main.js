const API_URL = "http://localhost:8000/api";

const perPage = 6;
let totalCount = 0;
let currentPage = 1;

function getPageFromUrl() {
  const params = new URLSearchParams(window.location.search);
  const raw = params.get("page");
  const page = raw ? Number(raw) : 1;
  return Number.isFinite(page) && page >= 1 ? page : 1;
}

function setPageInUrl(page) {
  const params = new URLSearchParams(window.location.search);
  params.set("page", String(page));
  const next = `${window.location.pathname}?${params.toString()}`;
  window.history.replaceState({}, "", next);
}

async function loadCars() {
    try {
        const response = await fetch(
            `${API_URL}/cars?page=${currentPage}&per_page=${perPage}`
        );
        const response_count = await fetch(
            `${API_URL}/cars`
        );
        const data = await response.json();

        totalCount = parseInt(response_count.headers.get("X-Total-Count")) || 0;

        renderCars(data);
        updatePagination();

    } catch (err) {
        console.error("Ошибка загрузки:", err);
    }
}

function renderCars(cars) {
    const container = document.getElementById("cars");
    container.innerHTML = "";

    if (!cars.length) {
        container.innerHTML = "<p>Нет автомобилей</p>";
        return;
    }

    cars.forEach(car => {
        const div = document.createElement("div");
        div.className = "card";

        div.innerHTML = `
            <h3>${car.name}</h3>
            <p>${car.brand}</p>
            <p>💰 Цена: ${car.price}</p>
            <p>📦 Остаток: ${car.stock}</p>
            <a href="/cars/${car.id}?page=${currentPage}">Подробнее</a>
        `;

        container.appendChild(div);
    });
}

function updatePagination() {
    const pageInfo = document.getElementById("page-info");
    const totalPages = Math.ceil(totalCount / perPage);

    pageInfo.textContent = `Страница ${currentPage} из ${totalPages}`;
}

function nextPage() {
    const totalPages = Math.ceil(totalCount / perPage);

    if (currentPage < totalPages) {
        currentPage++;
        setPageInUrl(currentPage);
        loadCars();
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        setPageInUrl(currentPage);
        loadCars();
    }
}

currentPage = getPageFromUrl();
setPageInUrl(currentPage);
loadCars();