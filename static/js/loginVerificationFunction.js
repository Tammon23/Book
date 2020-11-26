$(document).ready(function() {
	$('form').on('submit', function(event) {
	    event.preventDefault();
		$.ajax({
			data : {
				email : document.getElementById("InputEmail").value,
				password : document.getElementById("InputPassword").value
			},
			type : 'POST',
			url : '/verifyLogin'
		})
		.done(function(data) {
			if (data.error) {
				alert(data.error);
			}
			else {
//				$('form').submit();
                window.location.href = "/home";
			}
		});

	});
});