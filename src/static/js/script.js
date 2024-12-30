window.onload = () => {
    const button = document.getElementById("button");

    button.onclick = async () => {
        const body = {
            city_services: countCheckboxes("city_services"),
            housing_costs: countCheckboxes("housing_costs"),
            school_quality: countCheckboxes("school_quality"),
            local_policies: countCheckboxes("local_policies"),
            maintenance: countCheckboxes("maintenance"),
            social_events: countCheckboxes("social_events"),
        };

        if (Object.values(body).some(value => value === 0)) {
            displayError("Not all questions are answered. <br> Please answer all questions before submitting.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:8080/predict", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json; charset=UTF-8",
                },
                body: JSON.stringify(body),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            displayResults(result);
        } catch (error) {
            console.error("Error fetching prediction:", error);
            displayError("An error occurred while processing your request. <br> Please try again later.");
        }
    };
};

function countCheckboxes(elementId) {
    const container = document.getElementById(elementId);
    if (!container) {
        console.warn(`Element with id '${elementId}' not found.`);
        return 0;
    }

    const checkedStars = Array.from(container.children)
        .filter(el => el.checked && el.classList.contains("star"))
        .map(el => parseInt(el.className.split("-")[1], 10));

    return checkedStars.length > 0 ? checkedStars[0] : 0;
}

function displayResults(result) {
    const percentage = (100 * result.probability).toFixed(0);
    const popup = createPopup(result);

    popup.innerHTML = `
        <div class="popup-card">
            <h2 style="color:${result.prediction ? "green" : "red"};">
                ${result.prediction ?
                    `Good news - you are happy! We're ${percentage}% sure 😃` :
                    `Oh no, you seem to be unhappy! At least for ${percentage}% 😟`
                }
            </h2>
            <button class="close-popup" id="close-popup">Close</button>
        </div>
    `;

    document.body.appendChild(popup);
    document.getElementById("close-popup").onclick = () => popup.remove();
}

function displayError(message) {
    const popup = createPopup();

    popup.innerHTML = `
        <div class="popup-card">
            <h2 style="color:red;">
                ${message}
            </h2>
            <button id="close-popup">Close</button>
        </div>
    `;

    document.body.appendChild(popup);
    document.getElementById("close-popup").onclick = () => popup.remove();
}

function createPopup(result = null) {
    const popup = document.createElement("div");
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "#FD4";
    popup.style.border = "1px solid #ccc";
    popup.style.padding = "20px";
    popup.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
    popup.style.zIndex = "1000";
    popup.style.width = "800px";
    return popup;
}
