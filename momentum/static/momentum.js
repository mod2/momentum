var intervalId = -1;

$(document).ready(function() {
	// From https://gist.github.com/alanhamlett/6316427
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (settings.type == 'POST' || settings.type == 'PUT' || settings.type == 'DELETE' || settings.type == 'PATCH') {
				xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}
		}
	});

	function updateTimers() {
		$.ajax({
			url: '/status/',
			method: 'GET',
			data: {
				'key': webKey,
			},
			contentType: 'application/json',
			success: function(data) {
				data = JSON.parse(data);

				for (i in data) {
					var goal = data[i];
					var goalElement = $(".goal[data-slug=" + goal.slug + "]");

					if (goalElement.find(".button.stop").length > 0) {
						goalElement.find(".timer .num").html(goal.current_elapsed);
						goalElement.find(".timer .seconds").html(goal.current_elapsed_in_seconds);
						goalElement.find(".info .current").html(goal.current_amount);
					}
				}
			},
			error: function(data) {
				console.log("error", data);
			},
		});
	}

	function checkTimers() {
		if (intervalId == -1) {
			intervalId = setInterval(updateTimers, 1000);
		}
	}

	if ($(".goal .button.stop").length > 0) {
		checkTimers();
	}

	function toggleButtonClass(button, data) {
		if (button.hasClass("start")) {
			// Turn into a Stop button
			button.addClass("stop").removeClass("start");
			button.html("Stop");

			// Show the timer
			button.siblings(".timer").removeClass("hidden");

			checkTimers();
		} else if (button.hasClass("stop")) {
			// Turn into a Start button
			button.addClass("start").removeClass("stop");
			button.html("Start");

			// Hide the timer
			button.siblings(".timer").addClass("hidden");

			// Stop pinging the status web service if there aren't any more active timers
			if ($(".goal .button.stop").length == 0) {
				clearInterval(intervalId);
				intervalId = -1;
			}
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
					toggleButtonClass(button, data);
				},
				error: function(data) {
					console.log("error", data);
				},
			});
		}

		return false;
	});
});
