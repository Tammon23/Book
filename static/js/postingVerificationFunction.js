$(document).ready(function() {
	$('form').on('submit', function(event) {
	    event.preventDefault();
		$.ajax({
			data : {
			    BISBN : document.getElementById("enterISBN").value,
			    BTitle : document.getElementById("enterTitle").value,
			    BAuthor : document.getElementById("enterAuthor").value,
			    BCourse : document.getElementById("enterCourse").value,
			    BPrice : document.getElementById("enterPrice").value,
				BNumber : document.getElementById("enterQuantity").value,
				BDesc : document.getElementById("enterDesc").value
			},
			type : 'POST',
			url : '/verifyPosting'
		})
		.done(function(data) {
			if (data.error) {
				alert(data.error);
			}
			else {
                window.location.href = "/home";
			}
		});

	});
});