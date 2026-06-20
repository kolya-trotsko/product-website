$(document).ready(function() {
    $(document).on("click", ".conditioner-item", function(event) {
        const target = $(event.target);
        if (target.closest("input,button,label,a,form").length) {
            return;
        }
        var href = $(this).data("href");

        if (href) {
            window.location = href;
        } else {
            console.error("Missing data-href attribute for the clicked element.");
        }
    });
});
