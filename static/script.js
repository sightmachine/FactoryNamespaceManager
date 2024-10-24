const drawer = document.getElementById('drawer');
const closeIcon = document.getElementById('close-icon');
const drawerResizer = document.getElementById('drawer-resizer');
const submittedTable = document.getElementById('submitted-table');
const pageHeader = document.querySelector('.pageHeader');
let isResizing = false;
let lastY = 0;

function openDrawer() {
    drawer.style.display = 'block';
    drawer.style.height = '33%'; // Set default height
}

function toggleDrawer() {
    if (drawer.style.height === '55px') {
        drawer.style.height = '33%';
        document.getElementById('close-icon-path').setAttribute('d', 'M6 18L18 6M6 6l12 12'); // X icon
    } else {
        drawer.style.height = '55px';
        document.getElementById('close-icon-path').setAttribute('d', 'M6 9l6-6 6 6'); // Caret icon
    }
}

function resizeDrawer(e) {
    if (!isResizing) return;
    const newHeight = Math.max(55, Math.min(window.innerHeight - e.clientY, window.innerHeight - pageHeader.offsetHeight));
    drawer.style.height = newHeight + 'px';
}

function stopResizing() {
    isResizing = false;
}

drawerResizer.addEventListener('mousedown', (e) => {
    isResizing = true;
    lastY = e.clientY;
});

document.addEventListener('mousemove', resizeDrawer);
document.addEventListener('mouseup', stopResizing);

closeIcon.addEventListener('click', toggleDrawer);

function generateTable() {
    // Open the drawer when submit button is clicked
    openDrawer();

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
    // Clear previous table data
    submittedTable.innerHTML = '';


    // Create table header
    const headerRow = document.createElement('tr');
    ['Old Variable', 'Keywords', 'New Variable'].forEach(headerText => {
        const th = document.createElement('th');
        th.textContent = headerText;
        headerRow.appendChild(th);
    });
    submittedTable.appendChild(headerRow);

    // Populate table rows
    data.forEach(rowData => {
        const row = document.createElement('tr');
        rowData.forEach(cellData => {
            const td = document.createElement('td');
            td.textContent = cellData;
            row.appendChild(td);
        });
        submittedTable.appendChild(row);
    });
}

const historyButton = document.getElementById('history-button');
const historyModal = document.getElementById('history-modal');
const closeHistoryModal = document.getElementById('close-history-modal');
const modalBackdrop = document.getElementById('modal-backdrop');

const configButton = document.getElementById('configuration-button');
const configModal = document.getElementById('config-modal');
const closeConfigyModal = document.getElementById('close-config-modal');
const closeConfigyModal2 = document.getElementById('cancel-config-modal');
const modalbackdropConfig = document.getElementById('modal-backdropConfig');
const saveconfigButton = document.getElementById('save-config');


historyButton.addEventListener('click', () => {
    historyModal.style.display = 'block';
    modalBackdrop.style.display = 'block';
    fetchHistory();
});

closeHistoryModal.addEventListener('click', () => {
    historyModal.style.display = 'none';
    modalBackdrop.style.display = 'none';
});

modalBackdrop.addEventListener('click', () => {
    historyModal.style.display = 'none';
    modalBackdrop.style.display = 'none';
});

configButton.addEventListener('click', () => {
    configModal.style.display = 'block';
    modalbackdropConfig.style.display = 'block';
    loadConfig();
});

closeConfigyModal.addEventListener('click', () => {
    configModal.style.display = 'none';
    modalbackdropConfig.style.display = 'none';
});

closeConfigyModal2.addEventListener('click', () => {
    configModal.style.display = 'none';
    modalbackdropConfig.style.display = 'none';
});

modalbackdropConfig.addEventListener('click', () => {
    configModal.style.display = 'none';
    modalbackdropConfig.style.display = 'none';
});

saveconfigButton.addEventListener('click', () => {
    saveConfig();
    configModal.style.display = 'none';
    modalbackdropConfig.style.display = 'none';
});

function openLicense() {
    // Prevent default action of the link
    event.preventDefault();
    // Open the license.html in a new window
    window.open('/license', '_blank');
}

// Export to CSV functionality
document.getElementById('export-csv-button').addEventListener('click', () => {
    const rows = document.querySelectorAll('.data-table tbody tr');
    let csvContent = "data:text/csv;charset=utf-8,";

    // Add CSV headers
    csvContent += "Input Definition,New Name\n";

    // Iterate through each table row and append CSV data
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = Array.from(cells).map(cell => cell.textContent).join(',');
        csvContent += rowData + "\n";
    });

    // Create a download link and trigger the CSV download
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'exported_table.csv');
    document.body.appendChild(link); // Required for Firefox
    link.click();
    document.body.removeChild(link);
});

document.getElementById('export-json-button').addEventListener('click', () => {
    const rows = document.querySelectorAll('.data-table tbody tr');
    const jsonData = [];

    // Iterate through each table row to build the JSON array
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = {
            inputDefinition: cells[0].textContent,
            newName: cells[1].textContent
        };
        jsonData.push(rowData);
    });

    // Convert the JSON data to a string
    const jsonString = JSON.stringify(jsonData, null, 2); // Pretty print with 2 spaces

    // Create a Blob from the JSON string and generate a download link
    const blob = new Blob([jsonString], {type: 'application/json'});
    const url = URL.createObjectURL(blob);

    // Create a temporary link element for downloading
    const link = document.createElement('a');
    link.href = url;
    link.download = 'data.json'; // Filename for the downloaded file
    document.body.appendChild(link); // Append to the body
    link.click(); // Trigger the download
    document.body.removeChild(link); // Clean up
    URL.revokeObjectURL(url); // Free up memory
});

document.getElementById('submit-button').addEventListener('click', () => {

    document.getElementById("loader").style.display = "block";

    const userInput = document.getElementById('input-textarea').value;
    const renameTags = document.getElementById('rename-tags').value;
    const additionalInfo = document.getElementById('additional-info').value;
    const modelEndpointUrl = localStorage.getItem('modelEndpointUrl');
    const apiKey = localStorage.getItem('apiKey');

    fetch('/generate-table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            input: userInput,
            endpointurl: modelEndpointUrl,
            apikey: apiKey,
            rename_tags: renameTags,
            additional_info: additionalInfo
        }),
    })
        .then(response => response.json())
        .then(data => {
            document.getElementById("loader").style.display = "none";
            const tbody = document.querySelector('.data-table tbody');
            tbody.innerHTML = ''; // Clear any existing rows

            // Check if there is data to populate the table
            if (data && data.length > 0) {
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

                // Show the export buttons
                document.getElementById('export-json-button').style.display = 'inline-block';
                document.getElementById('export-csv-button').style.display = 'inline-block';
            } else {
                // Hide the export buttons if no data
                document.getElementById('export-json-button').style.display = 'none';
                document.getElementById('export-csv-button').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Hide the loader in case of an error as well
            document.getElementById("loader").style.display = "none";
        });
});

function fetchHistory() {
    fetch('/get-history')  // API call to fetch history
        .then(response => response.json())
        .then(data => {
            historyModal.innerHTML = '';

            const modalContent = document.createElement('div');
            modalContent.classList.add('modal-content');

            const closeButton = document.createElement('span');
            closeButton.id = 'close-history-modal';
            closeButton.innerHTML = '&times;';
            closeButton.onclick = () => {
                historyModal.style.display = 'none';
                modalBackdrop.style.display = 'none';
            };
            modalContent.appendChild(closeButton);

            // Loop through each history item and format it as needed
            data.history.forEach(item => {
                // Create a link element for each history entry
                const historyLink = document.createElement('a');
                historyLink.href = "#"; // You can set the appropriate URL or keep it empty if not needed

                // Create the div that contains the history entry details
                const historyDiv = document.createElement('div');
                historyDiv.classList.add('modal-body');
                historyDiv.innerHTML = item.description;  // Set the history description (e.g., "Bold Lion")

                // Create the timestamp element
                const timestamp = document.createElement('p');
                const timeSpan = document.createElement('span');
                timeSpan.style.fontSize = '11px';
                timeSpan.style.color = '#999';
                timeSpan.textContent = formatDate(item.timestamp); // Format the timestamp

                timestamp.appendChild(timeSpan);
                historyDiv.appendChild(timestamp);

                // Append the historyDiv to the link element
                historyLink.appendChild(historyDiv);

                // Add the link to the modal content
                modalContent.appendChild(historyLink);
            });

            historyModal.appendChild(modalContent);
            historyModal.style.display = 'block';
            modalBackdrop.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching history:', error);
        });
}

// Helper function to format the timestamp
function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
}

// Function to load saved configuration
function loadConfig() {
    const endpointUrl = localStorage.getItem('modelEndpointUrl');
    const apiKey = localStorage.getItem('apiKey');

    if (endpointUrl) {
        document.getElementById('endpoint-url').value = endpointUrl;
    }
    if (apiKey) {
        document.getElementById('api-key').value = apiKey;
    }
}

// Function to save configuration
function saveConfig() {
    const endpointUrl = document.getElementById('endpoint-url').value;
    const apiKey = document.getElementById('api-key').value;

    localStorage.setItem('modelEndpointUrl', endpointUrl);
    localStorage.setItem('apiKey', apiKey);
}
