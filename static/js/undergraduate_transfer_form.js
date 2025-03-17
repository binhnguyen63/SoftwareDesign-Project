// Need to call as website loads
window.onload = currentDate;

function addRowSearchContainer() {
    // Get the table reference
    let table = document.getElementById("transfer_equivalency");

    // Create a new row
    let newRow = table.insertRow(-1); // Inserts at the last position

    // Declare rows 
    let cols = [
        `<div class="search-container">
            <input type="text" name="transfer_institution">
            <span class="search-icon" onclick="searchFunction()">🔍</span>
        </div>`,
        `<div class="search-container">
            <input type="text" name="subject_area">
            <span class="search-icon" onclick="searchFunction()">🔍</span>
        </div>`,
        `<div class="search-container">
            <input type="text" name="transfer_number">
            <span class="search-icon" onclick="searchFunction()">🔍</span>
        </div>`,
        `<input type="text" name="course_title">`,
        `<input type="text" name="uh_subject_area" value="UH Subject" readonly>`,
        `<input type="text" name="catalog_number" value="Catalog Nbr" readonly>`,
        `<input type="text" name="grade" value="Grade" readonly>`,
        `<input type="text" name="credits_transferred" value="0.000000" readonly>`,
        `<input type="text" name="credits_taken" value="0.00" readonly>`,
    ];

    // Insert each column into the new row
    cols.forEach((col, index) => {
        let cell = newRow.insertCell(index);
        cell.innerHTML = col;
    });
}

function deleteRowSearchContainer(button) {
    let row = button.parentNode.parentNode; // Get the row
    let table = row.parentNode;
    if (table.rows.length > 2) { // Keep at least one row
        table.deleteRow(table.rows.length-1);
    }
}

function addRowAttachmentBox()
{
    // Get table 
    let table = document.getElementById("attachment-box");

    // Create rows
    let newRow = table.insertRow(-1); // Inserts at the last position

    // Declare rows
    let cols = [
        `<td></td>`,
        `<td><input type="file" id="attachments" name="attachments" accept="image/*" /></td>`,
        `<td>
                <select id="file-description" name="file-description">
                <option value="" selected>Select...</option>
                <option value="optional_supplemental_document">Optional Supplemental Document</option>
                <option value="petition_course_syllabus">Petition Course Syllabus</option>
                <option value="petition_course_description">Petition Course Description</option>
                <option value="transfer_credit_summary">Transfer Credit Summary</option>
        </td>`,
        `<td></td>`,
        `<td><button onclick="deleteRowAttachmentBox(this)">Delete</button></td>`
    ];

    // Insert column into the new row
    cols.forEach((col, index) => {
        let cell = newRow.insertCell(index);
        cell.innerHTML = col;
    });
}

function deleteRowAttachmentBox(button) {
    let row = button.closest("tr"); 
    let table = document.getElementById("attachment-box").getElementsByTagName('tbody')[0];

    if (table.rows.length > 1) { 
        row.remove(); 
    }
}

function currentDate()
{
    let myDate = new Date();
    let myMonth = myDate.getMonth() + 1;
    let myDay = myDate.getDate();
    let myYear = myDate.getFullYear();

    let todayDate = myMonth + "/" + myDay + "/" + myYear;

    document.getElementById("current_date").innerText = todayDate;
}

