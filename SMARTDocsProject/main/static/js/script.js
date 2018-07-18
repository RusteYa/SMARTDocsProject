const MESSAGES = {
	WARNING: 'warning',
	DANGER: 'danger',
	SUCCESS: 'success'
};

function get_cookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
			cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
};

$($.ajaxSetup({
	headers: {'X-CSRFToken': get_cookie('csrftoken')}, 
	dataType: 'json', 
	contetType: 'application/json',
	error: function(xhr, status, thrown) {
		display_message(thrown, MESSAGES.DANGER);
	}
}));

function get_calendar_config(multi) {
	return {
		autoUpdateInput: false,
		singleDatePicker: !multi,
		showDropdowns: !multi,
		locale: {
			cancelLabel: 'Отменить',
			applyLabel: 'Применить'
		}
	}
};

function display_message(message, type) {
	var $messages = $('.messages');
	$messages.append(
		$('<div></div>')
		.addClass('alert alert-'+type)
		.append(
			$('<a></a>')
			.addClass('close')
			.attr('data-dismiss', 'alert')
		).text(message)
	)
	if ($messages.children().length > 0) {
		$messages.slideDown(300);
		setTimeout(function() {
			$messages.slideUp(300);
			$messages.children().remove();
		}, 5000);
	}
};

function add_datepicker(element, date_range) {
	element.daterangepicker(
		get_calendar_config(date_range)
	).on('apply.daterangepicker', function(ev, picker) {
		if (date_range) {
			$(this).val(
				picker.startDate.format('DD.MM.YYYY') 
				+ ' - ' + 
				picker.endDate.format('DD.MM.YYYY')
			);
		} else {
			$(this).val(
				picker.startDate.format('DD.MM.YYYY')
			);
		}
	}).on('cancel.daterangepicker', function(ev, picker) {
		$(this).val('');
	});
};