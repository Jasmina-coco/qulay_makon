function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    if (window.innerWidth <= 768) {
        sidebar.classList.toggle("open");
    } else {
        sidebar.classList.toggle("collapsed");
    }
    document.getElementById("mainContent").classList.toggle("expanded");
}

function toggleLangMenu() {
    const menu = document.getElementById("langMenu");
    if (menu) {
        menu.classList.toggle("show");
    }
}

function toggleSection(btn) {
    const section = btn.closest(".nav-section");
    if (!section) return;
    section.classList.toggle("collapsed");

    const label = btn.querySelector(".nav-label")?.textContent.trim();
    const collapsed = JSON.parse(localStorage.getItem("sidebarSections") || "{}");
    if (label) {
        collapsed[label] = section.classList.contains("collapsed");
        localStorage.setItem("sidebarSections", JSON.stringify(collapsed));
    }
}

async function fetchJson(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`Server xatosi: ${response.status}`);
    }
    return response.json();
}

function setMainImage(productId, imageId) {
    fetchJson(`/admin-panel/products/${productId}/images/${imageId}/set-main/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
    })
        .then((data) => {
            if (data.success) {
                showToast("Asosiy rasm o'zgartirildi", "success");
                setTimeout(() => location.reload(), 500);
            }
        })
        .catch((err) => {
            console.warn("Xato:", err);
            showToast("Xatolik yuz berdi", "error");
        });
}

function deleteImage(productId, imageId) {
    if (!confirm("Rasmni o'chirishni tasdiqlaysizmi?")) return;
    fetchJson(`/admin-panel/products/${productId}/images/${imageId}/delete/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
    })
        .then((data) => {
            if (data.success) {
                const element = document.getElementById(`image-${imageId}`);
                if (element) element.remove();
                showToast("Rasm o'chirildi", "success");
            }
        })
        .catch((err) => {
            console.warn("Xato:", err);
            showToast("Xatolik yuz berdi", "error");
        });
}

function getCookie(name) {
    let v = null;
    if (document.cookie) {
        document.cookie.split(";").forEach((c) => {
            c = c.trim();
            if (c.startsWith(name + "=")) v = decodeURIComponent(c.substring(name.length + 1));
        });
    }
    return v;
}
const csrftoken = getCookie("csrftoken");

if (window.Chart) {
    Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = "#5a7a7a";
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
}

function updateOrderStatus(orderId, newStatus) {
    fetchJson(`/admin-panel/orders/${orderId}/update-status/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
        body: JSON.stringify({ status: newStatus }),
    })
        .then((data) => {
            if (data.success) {
                showToast("Status yangilandi", "success");
                setTimeout(() => location.reload(), 500);
            }
        })
        .catch((err) => {
            console.warn("Xato:", err);
            showToast("Xatolik yuz berdi", "error");
        });
}

function toggleUserActive(userId) {
    fetchJson(`/admin-panel/accounts/users/${userId}/toggle/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
    })
        .then((data) => {
            if (data.success) {
                showToast(data.message, "success");
                setTimeout(() => location.reload(), 500);
            }
        })
        .catch((err) => {
            console.warn("Xato:", err);
            showToast("Xatolik yuz berdi", "error");
        });
}

function approveSeller(sellerId) {
    fetchJson(`/admin-panel/accounts/sellers/${sellerId}/approve/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
    })
        .then((data) => {
            if (data.success) {
                showToast(data.message, "success");
                setTimeout(() => location.reload(), 500);
            }
        })
        .catch((err) => {
            console.warn("Xato:", err);
            showToast("Xatolik yuz berdi", "error");
        });
}

function confirmDelete(url, itemName) {
    document.getElementById("deleteItemName").textContent = itemName;
    document.getElementById("deleteConfirmBtn").onclick = () => {
        fetchJson(url, { method: "POST", headers: { "X-CSRFToken": csrftoken } })
            .then((data) => {
                if (data.success) {
                    showToast("O'chirildi", "success");
                    location.reload();
                }
            })
            .catch((err) => {
                console.warn("Xato:", err);
                showToast("Xatolik yuz berdi", "error");
            });
    };
    document.getElementById("deleteModal").style.display = "flex";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

function dismissTip(tipId) {
    const el = document.getElementById(tipId);
    if (el) {
        el.style.animation = "tipFadeOut 0.3s ease forwards";
        setTimeout(() => el.remove(), 300);
    }
    const dismissed = JSON.parse(localStorage.getItem("dismissedTips") || "[]");
    if (!dismissed.includes(tipId)) {
        dismissed.push(tipId);
        localStorage.setItem("dismissedTips", JSON.stringify(dismissed));
    }
}

function showToast(msg, type = "info") {
    const t = document.createElement("div");
    t.className = `toast toast-${type}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.classList.add("show"), 10);
    setTimeout(() => {
        t.classList.remove("show");
        setTimeout(() => t.remove(), 300);
    }, 3000);
}

function searchTable(inputId, tableId) {
    const f = document.getElementById(inputId).value.toLowerCase();
    document.querySelectorAll(`#${tableId} tbody tr`).forEach((r) => {
        r.style.display = r.textContent.toLowerCase().includes(f) ? "" : "none";
    });
}

function debounce(func, wait = 300) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

async function fetchAndReplace(url, targetSelector, pushState = true) {
    try {
        const response = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
        if (!response.ok) throw new Error(`Server xatosi: ${response.status}`);
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const newNode = doc.querySelector(targetSelector);
        const currentNode = document.querySelector(targetSelector);
        if (newNode && currentNode) {
            currentNode.innerHTML = newNode.innerHTML;
            if (pushState) window.history.pushState({}, "", url);
            bindAjaxFilters();
        }
    } catch (err) {
        console.warn("Xato:", err);
        showToast("Ma'lumot yuklashda xato", "error");
    }
}

function bindAjaxFilters() {
    document.querySelectorAll('form[data-ajax-filter="true"]').forEach((form) => {
        if (form.dataset.bound === "1") return;
        form.dataset.bound = "1";
        const targetSelector = form.dataset.target;

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const params = new URLSearchParams(new FormData(form)).toString();
            const url = `${window.location.pathname}${params ? `?${params}` : ""}`;
            await fetchAndReplace(url, targetSelector);
        });

        form.querySelectorAll("select").forEach((select) => {
            select.addEventListener("change", () => form.requestSubmit());
        });
    });

    document.querySelectorAll('[id$="Container"] .pagination a').forEach((link) => {
        if (link.dataset.bound === "1") return;
        link.dataset.bound = "1";
        link.addEventListener("click", async (e) => {
            const container = e.target.closest('[id$="Container"]');
            if (!container) return;
            e.preventDefault();
            await fetchAndReplace(link.href, `#${container.id}`);
        });
    });

    document.querySelectorAll(".status-select").forEach((select) => {
        if (select.dataset.bound === "1") return;
        select.dataset.bound = "1";
        select.addEventListener("change", () => {
            updateOrderStatus(select.dataset.orderId, select.value);
        });
    });
}

function renderGlobalSearchResults(items) {
    const resultsEl = document.getElementById("globalSearchResults");
    if (!resultsEl) return;
    if (!items.length) {
        resultsEl.innerHTML = '<div class="search-empty">No results</div>';
        resultsEl.classList.add("show");
        return;
    }
    resultsEl.innerHTML = items
        .map(
            (item) => `
            <a href="${item.url}" class="search-item">
                <div class="search-item-title">${item.title}</div>
                <div class="search-item-meta">${item.type} - ${item.subtitle}</div>
            </a>
        `
        )
        .join("");
    resultsEl.classList.add("show");
}

document.addEventListener("DOMContentLoaded", () => {
    const dismissed = JSON.parse(localStorage.getItem("dismissedTips") || "[]");
    dismissed.forEach((tipId) => {
        const el = document.getElementById(tipId);
        if (el) el.remove();
    });

    const collapsed = JSON.parse(localStorage.getItem("sidebarSections") || "{}");
    document.querySelectorAll(".nav-section").forEach((section) => {
        const label = section.querySelector(".nav-label")?.textContent.trim();
        const hasActive = section.querySelector(".nav-link.active");

        if (hasActive) {
            section.classList.remove("collapsed");
        } else if (label && collapsed[label]) {
            section.classList.add("collapsed");
        }
    });

    bindAjaxFilters();

    const globalSearchInput = document.getElementById("globalSearchInput");
    const globalSearchResults = document.getElementById("globalSearchResults");
    if (globalSearchInput && globalSearchResults) {
        const searchUrl = globalSearchInput.dataset.searchUrl;
        const handleSearch = debounce(async () => {
            const q = globalSearchInput.value.trim();
            if (q.length < 2) {
                globalSearchResults.classList.remove("show");
                globalSearchResults.innerHTML = "";
                return;
            }
            try {
                const payload = await fetchJson(`${searchUrl}?q=${encodeURIComponent(q)}`);
                renderGlobalSearchResults(payload.results || []);
            } catch (err) {
                console.warn("Xato:", err);
                globalSearchResults.innerHTML = '<div class="search-empty">Xatolik yuz berdi</div>';
                globalSearchResults.classList.add("show");
            }
        }, 250);
        globalSearchInput.addEventListener("input", handleSearch);
    }

    document.addEventListener("click", function (e) {
        const dropdown = document.querySelector(".lang-dropdown");
        const menu = document.getElementById("langMenu");
        const searchBox = document.querySelector(".search-box");
        if (dropdown && menu && !dropdown.contains(e.target)) {
            menu.classList.remove("show");
        }
        if (searchBox && !searchBox.contains(e.target)) {
            const panel = document.getElementById("globalSearchResults");
            if (panel) panel.classList.remove("show");
        }
    });
});
