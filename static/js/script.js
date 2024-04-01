// Update page number
function setPageNumber() {
    var pageNumberElements = document.querySelectorAll('.page-number');
    var totalPages = getTotalPages(); // You need to implement this function
    pageNumberElements.forEach(function (element) {
        element.textContent = "Page " + totalPages;
    });
}

// You need to implement this function to get total number of pages
function getTotalPages() {
    // Logic to calculate total pages
    return 2; // For example, assuming there are 10 pages
}

// Call setPageNumber when document is loaded
document.addEventListener("DOMContentLoaded", function () {
    setPageNumber();
});
