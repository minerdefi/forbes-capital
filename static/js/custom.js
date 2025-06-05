// Light/Dark Mode Toggle
const themeToggleButton = document.getElementById('theme-toggle');
const themeToggleIcon = document.getElementById('theme-toggle-icon');

function updateTheme() {
    if (localStorage.getItem('theme') === 'dark') {
        document.documentElement.classList.add('dark');
        themeToggleIcon.classList.remove('fa-moon');
        themeToggleIcon.classList.add('fa-sun');
    } else {
        document.documentElement.classList.remove('dark');
        themeToggleIcon.classList.remove('fa-sun');
        themeToggleIcon.classList.add('fa-moon');
    }
}

themeToggleButton.addEventListener('click', () => {
    if (localStorage.getItem('theme') === 'dark') {
        localStorage.setItem('theme', 'light');
    } else {
        localStorage.setItem('theme', 'dark');
    }
    updateTheme();
});

// Initial theme setup
if (localStorage.getItem('theme') === null) {
    localStorage.setItem('theme', window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}
updateTheme();

// Mobile Menu Toggle
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileMenu = document.getElementById('mobile-menu');

mobileMenuButton.addEventListener('click', () => {
    mobileMenu.classList.toggle('hidden');
});


function toggleBio(button) {
    const bioSection = button.closest('div').nextElementSibling.nextElementSibling;
    bioSection.classList.toggle('hidden');
    button.querySelector('span').textContent = bioSection.classList.contains('hidden') ? '+' : '-';
}

document.addEventListener("DOMContentLoaded", function () {
    const alertBox = document.getElementById('alert');
    const closeBtn = document.getElementById('close-btn');

    // Show the alert
    setTimeout(() => {
        alertBox.classList.remove('hidden');
    }, 500);

    // Hide the alert when the close button is clicked
    closeBtn.addEventListener('click', () => {
        alertBox.classList.add('hidden');
    });
});

function toggleDetails(row) {
    const nextRow = row.nextElementSibling;
    if (nextRow && nextRow.tagName === 'TR') {
        const detailsCell = nextRow.querySelector('td');
        if (detailsCell) {
            detailsCell.classList.toggle('hidden');
        }
    }
}



document.addEventListener('DOMContentLoaded', function () {
    const dropdownButton = document.getElementById('dropdownButton1');
    const dropdownMenu = document.getElementById('dropdownMenu1');
    const selectedOption = document.getElementById('selectedOption');
    const mobileTableBody = document.getElementById('mobileTableBody');
    const mobileHeader = document.getElementById('mobileHeader');

    const rows = [
        { name: 'Bitcoin', weight: '71.9%', marketCap: '$1,266,887,701,017', price: '$64,210.14', change: '-0.0%' },
        { name: 'Ethereum', weight: '19.0%', marketCap: '$332,745,940,307', price: '$2,767.48', change: '-1.0%' },
        // Add more rows as needed
    ];

    dropdownButton.addEventListener('click', function () {
        // Toggle dropdown visibility
        dropdownMenu.classList.toggle('hidden');
    });

    dropdownMenu.addEventListener('click', function (event) {
        if (event.target.tagName === 'A') {
            const value = event.target.getAttribute('data-value');
            const text = event.target.textContent;

            // Update the selected option text
            selectedOption.textContent = text;

            // Update the mobile table
            updateMobileTable(value);

            // Close the dropdown menu
            dropdownMenu.classList.add('hidden');

            // Prevent page scroll jump
            event.preventDefault();
        }
    });

    function updateMobileTable(option) {
        let mobileRows = '';

        rows.forEach(row => {
            let cellValue;
            switch (option) {
                case 'weight':
                    cellValue = row.weight;
                    break;
                case 'marketCap':
                    cellValue = row.marketCap;
                    break;
                case 'price':
                    cellValue = row.price;
                    break;
                case 'change':
                    cellValue = row.change;
                    break;
                default:
                    cellValue = row.weight; // Default to weight if something goes wrong
            }

            mobileRows += `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap">${row.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${cellValue}</td>
                </tr>
            `;
        });

        mobileTableBody.innerHTML = mobileRows;
        mobileHeader.textContent = text;
    }
});
