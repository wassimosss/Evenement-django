
    document.addEventListener("DOMContentLoaded", function () {
        const cardInput = document.getElementById("card_number");
        const iconSpan = document.getElementById("card-icon");
        const paymentModeSelect = document.getElementById("payment_mode");

        cardInput.addEventListener("input", function () {
            const value = cardInput.value.replace(/\s+/g, "");
            if (/^4/.test(value)) {
                iconSpan.className = "bi bi-credit-card-fill card-icon text-primary";
                paymentModeSelect.value = "visa";
            } else if (/^5[1-5]/.test(value)) {
                iconSpan.className = "bi bi-credit-card-2-front-fill card-icon text-warning";
                paymentModeSelect.value = "mastercard";
            } else {
                iconSpan.className = "bi bi-credit-card card-icon text-muted";
                paymentModeSelect.value = "";
            }
        });

        const monthSelect = document.getElementById("expiry_month");
        for (let m = 1; m <= 12; m++) {
            let value = m < 10 ? "0" + m : m;
            let option = new Option(value, value);
            monthSelect.add(option);
        }

        const yearSelect = document.getElementById("expiry_year");
        const currentYear = new Date().getFullYear();
        for (let y = currentYear; y <= currentYear + 10; y++) {
            let option = new Option(y, y);
            yearSelect.add(option);
        }

        const form = document.querySelector("form");
        form.addEventListener("submit", function (e) {
            const selectedMonth = parseInt(monthSelect.value);
            const selectedYear = parseInt(yearSelect.value);
            const today = new Date();
            const currentMonth = today.getMonth() + 1;
            const currentYear = today.getFullYear();

            if (
                selectedYear < currentYear ||
                (selectedYear === currentYear && selectedMonth < currentMonth)
            ) {
                e.preventDefault();
                alert("La date d'expiration doit être actuelle ou future.");
            }
        });
    });
