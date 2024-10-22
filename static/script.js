function generateTable() {
    const tbody = document.querySelector('.data-table tbody');
    tbody.innerHTML = ''; // Clear any existing rows
    for (let i = 0; i < 55; i++) {
        const row = document.createElement('tr');
        for (let j = 0; j < 21; j++) {
            const cell = document.createElement('td');
            cell.textContent = `Row ${i + 1}, Cell ${j + 1}`; // Sample cell content
            row.appendChild(cell);
        }
        tbody.appendChild(row);
    }
    document.getElementById('table-container').style.display = 'block'; // Show the table
    document.getElementById('drawer').style.display = 'block'; // Show the drawer
}

const resizer = document.getElementById('resizer');
const drawer = document.getElementById('drawer');
const caretIcon = document.getElementById('caret-icon');
const caretPath = document.getElementById('caret-path');
let isResizing = false;

resizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', stopResizing);
});

const handleMouseMove = (e) => {
    if (!isResizing) return;
    const newHeight = Math.max(55, window.innerHeight - e.clientY); // Minimum height is 55px
    drawer.style.height = newHeight + 'px';
};

const stopResizing = () => {
    isResizing = false;
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', stopResizing);
};

// Collapse/expand functionality
let isCollapsed = false;

document.getElementById('close-icon').addEventListener('click', () => {
    if (isCollapsed) {
        drawer.style.height = '610px'; // Restore height
        caretPath.setAttribute('d', 'M12 16l-6-6h12l-6 6z'); // Caret down
    } else {
        drawer.style.height = '55px'; // Collapse height
        caretPath.setAttribute('d', 'M12 8l-6 6h12l-6-6z'); // Caret up
    }
    isCollapsed = !isCollapsed;
});

// Modal functionality
const historyButton = document.getElementById('history-button');
const modal = document.getElementById('modal');
const modalBackdrop = document.getElementById('modal-backdrop');
const closeModal = document.getElementById('close-modal');

historyButton.addEventListener('click', () => {
    modal.style.display = 'block'; // Show modal
    modalBackdrop.style.display = 'block'; // Show backdrop
});

closeModal.addEventListener('click', () => {
    modal.style.display = 'none'; // Hide modal
    modalBackdrop.style.display = 'none'; // Hide backdrop
});

modalBackdrop.addEventListener('click', () => {
    modal.style.display = 'none'; // Hide modal
    modalBackdrop.style.display = 'none'; // Hide backdrop
});

document.getElementById('export-csv-button').addEventListener('click', () => {
    fetch('/export-csv')
        .then(response => response.blob()) // Convert response to a blob (file-like object)
        .then(blob => {
            // Create a link element to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'data.csv'; // Default CSV filename
            document.body.appendChild(a);
            a.click(); // Programmatically click the link to trigger download
            a.remove(); // Remove the link after download
        })
        .catch(error => console.error('Error exporting CSV:', error));
});


document.getElementById('export-json-button').addEventListener('click', () => {
    fetch('/export-json')
        .then(response => response.blob()) // Convert response to a blob (file-like object)
        .then(blob => {
            // Create a link element to download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'data.json'; // Default JSON filename
            document.body.appendChild(a);
            a.click(); // Programmatically click the link to trigger download
            a.remove(); // Remove the link after download
        })
        .catch(error => console.error('Error exporting JSON:', error));
});

document.getElementById('submit-button').addEventListener('click', () => {
    const userInput = document.getElementById('input-textarea').value;

    fetch('/generate-table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = ''; // Clear any existing rows

        // Iterate through the returned data and populate the table
        data.forEach(row => {
            const tr = document.createElement('tr');

            // Create "Input definition" column
            const tdInputDef = document.createElement('td');
            tdInputDef.textContent = row.input_definition;
            tr.appendChild(tdInputDef);

            // Create "New name" column (blank for now)
            const tdNewName = document.createElement('td');
            tdNewName.textContent = row.new_name || ''; // Empty string for blank new name
            tr.appendChild(tdNewName);

            tbody.appendChild(tr);
        });

        // Show the table and drawer
        document.getElementById('table-container').style.display = 'block';
        document.getElementById('drawer').style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
});
