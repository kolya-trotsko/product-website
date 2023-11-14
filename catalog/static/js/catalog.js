$(document).ready(function() {
    $(document).on("click", ".conditioner-item", function() {
        var href = $(this).data("href");

        if (href) {
            window.location = href;
        } else {
            console.error("Missing data-href attribute for the clicked element.");
        }
    });
});
