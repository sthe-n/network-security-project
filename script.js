    const report = "static/documents/Introduction to Network Security.pdf";

    document.getElementById("downloadpdf").addEventListener("click", function () {
    const link = document.createElement("a");
    link.href = report;
    link.download = "Introduction to Network Security.pdf";
    link.click();
});

