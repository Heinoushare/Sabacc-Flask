$(document).ready(function() {


	$(".link").on("click", function() {

        /* Get the text field */
        let link = $(this).attr("id");

        /* Select the text field */
        // link.select();
        // link.setSelectionRange(0, 99999); /* For mobile devices */

        /* Copy the text inside the text field */
        navigator.clipboard.writeText(link);

        /* Alert the copied text */
        alert("Copied the text: " + link);
        console.log(link);

    });

});