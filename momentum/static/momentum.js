$(document).ready(function() {
	// From https://gist.github.com/alanhamlett/6316427
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE' || settings.type == 'PATCH') {
				xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}
		}
	});


	function toggleButtonClass(button) {
		if (button.hasClass("start")) {
			// Turn into a Stop button
			button.addClass("stop").removeClass("start");
			button.html("Stop");

			// Show the timer
			button.siblings(".timer").removeClass("hidden");
		} else if (button.hasClass("stop")) {
			// Turn into a Start button
			button.addClass("start").removeClass("stop");
			button.html("Start");

			// Hide the timer
			button.siblings(".timer").addClass("hidden");
		}
	}

	// Start/stop buttons
	$(".button").on("click touchstart", function() {
		// Get the slug of the goal we want
		var goalSlug = $(this).parents(".goal").attr("data-slug");
		var button = $(this);

		if (goalSlug != '') {
			// Send in the timer request
			// It's GET so we can use it in Launch Center Pro, Drafts, etc.
			$.ajax({
				url: '/' + goalSlug + '/timer/',
				method: 'GET',
				data: {
					'key': webKey,
				},
				contentType: 'application/json',
				success: function(data) {
					data = JSON.parse(data);
					toggleButtonClass(button);
				},
				error: function(data) {
					console.log("error", data);
				},
			});
		}
	});
});
