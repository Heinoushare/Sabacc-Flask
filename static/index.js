$(document).ready(function() {


	$(".link").on("click", function() {

        /* Get the text field */
        let link = $(this).attr("id");

        /* Copy the text inside the text field */
        navigator.clipboard.writeText(link);

        /* Alert the copied text */
        document.getElementById(link).innerHTML = "Copied!";
        document.getElementById(link).setAttribute("class", document.getElementById(link).getAttribute("class") + " green");

    });

});