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
						goalElement.find(".percentage .bar").css("width", goal.current_percentage + "%");

						if (goal.current_amount > parseFloat(goalElement.find(".info .target").html())) {
							goalElement.find(".percentage .bar").addClass("over");
						}
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

		// Update the favicon
		updateFavicon("timer");
	}

	function updateFavicon(type) {
		var dataHref = "data-" + type + "-href";

		var oldIco = $("#favicon-ico");
		var oldPng = $("#favicon-png");

		var newIco = "<link id='favicon-ico' rel='shortcut icon' href='" + oldIco.attr(dataHref) + "' data-original-href='" + oldIco.attr("data-original-href") + "' data-timer-href='" + oldIco.attr("data-timer-href") + "' />";
		var newPng = "<link id='favicon-png' rel='shortcut icon' href='" + oldPng.attr(dataHref) + "' data-original-href='" + oldPng.attr("data-original-href") + "' data-timer-href='" + oldPng.attr("data-timer-href") + "' />";

		oldIco.remove();
		oldPng.remove();

		$("head").append(newIco);
		$("head").append(newPng);
	}

	function toggleButtonClass(button, data) {
		if (button.hasClass("start")) {
			// Turn into a Stop button
			button.addClass("stop").removeClass("start");
			button.find(".label").html("Stop");

			// Show the timer
			button.find(".timer").removeClass("hidden");

			// Set it running
			button.parents(".goal").addClass("running");

			// Update the favicon
			updateFavicon("timer");

			checkTimers();
		} else if (button.hasClass("stop")) {
			// Turn into a Start button
			button.addClass("start").removeClass("stop");
			button.find(".label").html("Start");

			// Hide the timer
			button.find(".timer").addClass("hidden");

			// Stop it running
			button.parents(".goal").removeClass("running");

			// Stop pinging the status web service if there aren't any more active timers
			if ($(".goal .button.stop").length == 0) {
				clearInterval(intervalId);
				intervalId = -1;

				// Change the favicon back
				updateFavicon("original");
			}
		}
	}

	// Start/stop buttons
	$(".button.action").on("click touchstart", function() {
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


	// Wordcount entry
	$(".entry.action .save").on("click touchstart", function() {
		// Get the slug of the goal we want
		var goalSlug = $(this).parents(".goal").attr("data-slug");

		var parentWrapper = $(this).parents(".entry.action");
		var amount = $(this).siblings("input[type=number]").val();

		if (goalSlug != '' && amount > 0) {
			// Send in the request
			$.ajax({
				url: '/' + goalSlug + '/save/',
				method: 'GET',
				data: {
					'key': webKey,
					'amount': amount,
				},
				contentType: 'application/json',
				success: function(data) {
					data = JSON.parse(data);

					if (data.status == 'success') {
						// Update count
						var goalElement = parentWrapper.parents(".goal");
						goalElement.find(".info .current").html(data.total_amount);
						goalElement.find(".percentage .bar").css("width", data.percentage + "%");

						if (data.total_amount > parseInt(goalElement.find(".info .target").html())) {
							goalElement.find(".percentage .bar").addClass("over");
						}

						// Clear out the input
						parentWrapper.find("input[type=number]").val('');
					} else {
						parentWrapper.addClass("error");
					}
				},
				error: function(data) {
					console.log("error", data);
				},
			});
		}

		return false;
	});


	// Reordering goals
	$("#goal-list").sortable({
		placeholder: "goal container placeholder",
		update: function(event, ui) {
			var order = {};
			var items = ui.item.parents("#goal-list").find(".goal");

			for (var i=0; i<items.length; i++) {
				var item = $(items[i]);
				order[item.attr("data-slug")] = i + 1;
			}

			var url = '/update-goals/';

			$.ajax({
				url: url,
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ "order": order }),
				success: function(data) {
				},
				error: function(data) {
					console.log("Error! :(", data);
				},
			});
		},
	});
});

// From https://gist.github.com/alanhamlett/6316427
function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i=0; i<cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
