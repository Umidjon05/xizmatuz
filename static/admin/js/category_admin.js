document.addEventListener('DOMContentLoaded', function () {
    const iconMap = {
        "Uy xizmatlari": "🏠",
        "Oila yordami": "👨‍👩‍👧",
        "Transport": "🚗",
        "Texnik xizmat": "💻",
        "Go'zallik saloni": "💄",
    };

    const parentSelect = document.getElementById('id_parent');
    const iconInput = document.getElementById('id_icon');

    if (parentSelect && iconInput) {
        parentSelect.addEventListener('change', function () {
            const selectedText = parentSelect.options[parentSelect.selectedIndex].text;
            if (iconMap[selectedText]) {
                iconInput.value = iconMap[selectedText];
            }
        });
    }
});
