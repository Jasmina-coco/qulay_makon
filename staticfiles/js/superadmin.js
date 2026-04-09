function saGetCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i += 1) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(`${name}=`)) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const saCsrfToken = saGetCookie("csrftoken");

if (window.Chart) {
    // Light theme uchun Chart.js defaults
    Chart.defaults.color = "#9AA0B4";
    Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.scale.grid.color = "rgba(0, 0, 0, 0.04)";
}

const chartColors = {
    primary: "#3E53A0",
    primaryLight: "#5A77DF",
    success: "#22C55E",
    warning: "#F59E0B",
    danger: "#EF4444",
    info: "#3B82F6",
    purple: "#8B5CF6",
};

const revenueDatasetConfig = {
    borderColor: chartColors.primary,
    backgroundColor: "rgba(62, 83, 160, 0.06)",
    pointBackgroundColor: chartColors.primary,
    pointBorderColor: "#fff",
    pointBorderWidth: 2,
    pointRadius: 4,
    pointHoverRadius: 6,
    tension: 0.4,
    fill: true,
    borderWidth: 2,
};

const commissionDatasetConfig = {
    borderColor: chartColors.success,
    backgroundColor: "rgba(34, 197, 94, 0.06)",
    pointBackgroundColor: chartColors.success,
    pointBorderColor: "#fff",
    pointBorderWidth: 2,
    pointRadius: 4,
    tension: 0.4,
    fill: true,
    borderWidth: 2,
};

const doughnutColors = [
    chartColors.primary,
    chartColors.primaryLight,
    chartColors.success,
    chartColors.warning,
    chartColors.danger,
];

const barConfig = {
    backgroundColor: chartColors.primary,
    borderRadius: 6,
    barThickness: 16,
};

function saConfirmAndDelete(url, message = "Delete item?") {
    if (!confirm(message)) return;
    fetch(url, { method: "POST", headers: { "X-CSRFToken": saCsrfToken } })
        .then((r) => r.json())
        .then((data) => {
            if (data.success) {
                window.location.reload();
            } else if (data.error) {
                alert(data.error);
            }
        });
}

function saToggleStatus(url) {
    fetch(url, { method: "POST", headers: { "X-CSRFToken": saCsrfToken } })
        .then((r) => r.json())
        .then((data) => {
            if (data.success) {
                window.location.reload();
            } else if (data.error) {
                alert(data.error);
            }
        });
}

async function saLoadDashboardCharts() {
    const revenueCanvas = document.getElementById("saRevenueChart");
    const dailyOrdersCanvas = document.getElementById("saDailyOrdersChart");
    const sellersRevenueCanvas = document.getElementById("saSellersRevenueChart");
    const usersCanvas = document.getElementById("saUsersChart");
    if (!revenueCanvas && !dailyOrdersCanvas && !sellersRevenueCanvas && !usersCanvas) return;

    if (revenueCanvas) {
        const data = await fetch("/super-admin/api/revenue/").then((r) => r.json());
        new Chart(revenueCanvas, {
            type: "line",
            data: {
                labels: data.map((d) => d.month),
                datasets: [
                    {
                        label: "Daromad",
                        data: data.map((d) => d.revenue),
                        ...revenueDatasetConfig,
                    },
                    {
                        label: "Komissiya",
                        data: data.map((d) => d.commission),
                        ...commissionDatasetConfig,
                    },
                ],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    }

    if (dailyOrdersCanvas) {
        const data = await fetch("/super-admin/api/daily-orders/").then((r) => r.json());
        new Chart(dailyOrdersCanvas, {
            type: "bar",
            data: {
                labels: data.map((d) => d.day),
                datasets: [
                    {
                        label: "Buyurtmalar",
                        data: data.map((d) => d.count),
                        ...barConfig,
                        backgroundColor: chartColors.info,
                    },
                ],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    }

    if (sellersRevenueCanvas) {
        const data = await fetch("/super-admin/api/sellers-revenue/").then((r) => r.json());
        new Chart(sellersRevenueCanvas, {
            type: "bar",
            data: {
                labels: data.map((d) => d.product__seller__username || "N/A"),
                datasets: [
                    {
                        label: "Top sotuvchilar",
                        data: data.map((d) => Number(d.total || 0)),
                        ...barConfig,
                    },
                ],
            },
            options: { indexAxis: "y", responsive: true, maintainAspectRatio: false },
        });
    }

    if (usersCanvas) {
        const data = await fetch("/super-admin/api/users-analytics/").then((r) => r.json());
        new Chart(usersCanvas, {
            type: "line",
            data: {
                labels: data.map((d) => d.month),
                datasets: [
                    {
                        label: "Yangi foydalanuvchilar",
                        data: data.map((d) => d.count),
                        ...revenueDatasetConfig,
                        borderColor: chartColors.purple,
                        pointBackgroundColor: chartColors.purple,
                        backgroundColor: "rgba(139, 92, 246, 0.08)",
                    },
                ],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    saLoadDashboardCharts();
});
