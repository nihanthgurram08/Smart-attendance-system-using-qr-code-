// scan.js - Smart Attendance System

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const qrInput = document.querySelector("textarea");

    if (!form || !qrInput) return;

    form.addEventListener("submit", function (event) {
        // Prevent empty submission
        if (qrInput.value.trim() === "") {
            alert("Please paste QR code data before submitting.");
            event.preventDefault();
            return;
        }

        // Prevent duplicate attendance for the same QR (basic client-side check)
        const markedKey = "attendance_marked_" + qrInput.value.trim();
        if (sessionStorage.getItem(markedKey)) {
            alert("Attendance already submitted for this session.");
            event.preventDefault();
            return;
        }

        // Mark attendance as submitted
        sessionStorage.setItem(markedKey, "true");
    });
});
