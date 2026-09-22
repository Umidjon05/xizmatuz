function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return '';
}

function detectLocation() {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(function (position) {
        const lat = position.coords.latitude;
        const lon = position.coords.longitude;

        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
            .then(res => res.json())
            .then(data => {
                const address = data.address || {};
                const city = address.city || address.town || address.village || address.state || '';

                if (city) {
                    fetch('/accounts/save-location/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': getCSRFToken(),
                        },
                        body: `city=${encodeURIComponent(city)}`
                    });
                }
            });
    });
}

document.addEventListener('DOMContentLoaded', detectLocation);
