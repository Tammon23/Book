$(document).ready(function() {
	$('form').on('submit', function(event) {
	    event.preventDefault();
		$.ajax({
			data : {
				email : document.getElementById("exampleInputEmail1").value,
				username : document.getElementById("userName1").value,
				password : document.getElementById("exampleInputPassword1").value,
				confirm_password : document.getElementById("exampleInputPassword2").value
			},
			type : 'POST',
			url : '/verifySignUp'
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