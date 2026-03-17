const API_URL = "http://localhost:8000/api"; // поменяй если нужно

let currentPage = 1;
const perPage = 2;
let totalCount = 0;

async function loadCars() {
    try {
        const response = await fetch(
            `${API_URL}/cars?page=${currentPage}&per_page=${perPage}`
        );
        const response_count = await fetch(
            `${API_URL}/cars`
        );
        const data = await response.json();

        // общее количество
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
            <p>💰 Цена: ${car.price}</p>
            <p>📦 Остаток: ${car.stock}</p>
            <a href="/cars/${car.id}">Подробнее</a>
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
        loadCars();
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadCars();
    }
}

// загрузка при старте
loadCars();