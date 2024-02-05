window.onload = function() {

    let button = document.getElementById("button")
    button.onclick = () => {

        var city_services = count_checkboxes("city_services")
        var housing_costs = count_checkboxes("housing_costs")
        var school_quality = count_checkboxes("school_quality")
        var local_policies = count_checkboxes("local_policies")
        var maintenance = count_checkboxes("maintenance")
        var social_events = count_checkboxes("social_events")

        var body = {
            city_services: city_services,
            housing_costs: housing_costs,
            school_quality: school_quality,
            local_policies: local_policies,
            maintenance: maintenance,
            social_events: social_events
        }

        fetch("http://localhost:8080/predict", {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
                }
            }
        )
        .then(response => response.json())
        .then(json => result = json)
        .then(() => {
            percentage = (100 * result.probability).toFixed(0)
            if (result.prediction) {
                results.innerHTML = `
                <div class="card">
                <h2><font size="5" color="green">Good news - you are happy! We're ${percentage}% sure &#128512;</font></h2>
                </div>
            `;
            } else {
                results.innerHTML = `
                <div class="card">
                <h2><font size="5" color="red">Oh no, you seem to be unhappy! At least for ${percentage}% &#128543;</font></h2>
                </div>
            `;
            }

            });
    }
}

function count_checkboxes(elementId){
    boxes = document.getElementById(elementId)
    var stars = 0;
    for (let element of boxes.children) {
        if(element.className == "star star-5" && element.checked){
            stars = 5;
            break;
        }
        if(element.className == "star star-4" && element.checked){
            stars = 4;
            break;
        }
        if(element.className == "star star-3" && element.checked){
            stars = 3;
            break;
        }
        if(element.className == "star star-2" && element.checked){
            stars = 2;
            break;
        }
        if(element.className == "star star-1" && element.checked){
            stars = 1;
            break;
        }

    };
    return stars;
}
