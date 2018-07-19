const MESSAGES = {
	WARNING: 'warning',
	DANGER: 'danger',
	SUCCESS: 'success'
};

function createElement(elementName) {
	return $('<'+elementName+'></'+elementName+'>');
};

function createAlert(text, type) {
	var div = createElement('div');
	var a = createElement('a');
	div.addClass('alert alert-'+type);
	div.css('display', 'none');
	div.text(text);
	return div;
};

function displayMessage(message, type) {
	var $messages = $('.messages');
	$messages.append(createAlert(message, type));
	$messages.slideDown(200);
	if ($messages.children().length > 0) {
		$messages.children().last().slideDown(500);
		setTimeout(function() {
			$messages.children().first().slideUp(500);
			setTimeout(function() {
				$messages.children().first().remove();
			}, 500);
		}, 5000);
	} else {
		$messages.slideUp(200);
	}
};

function getCookie(name) {
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
	headers: {'X-CSRFToken': getCookie('csrftoken')}, 
	dataType: 'json', 
	contetType: 'application/json',
	error: function(xhr, status, thrown) {
		displayMessage(thrown, MESSAGES.DANGER);
	}
}));

function getCalendarConfig(isSingle=true) {
	return {
		autoUpdateInput: false,
		singleDatePicker: isSingle,
		showDropdowns: isSingle,
		locale: {
			cancelLabel: 'Отменить',
			applyLabel: 'Применить'
		}
	};
};

function onDatePickerApply(evt, picker) {
	var value = picker.startDate.format('DD.MM.YYYY');
	if (!picker.singleDatePicker) {
		value = 
			picker.startDate.format('DD.MM.YYYY')
			+' - '+
			picker.endDate.format('DD.MM.YYYY');
	}
	$(this).val(value);
};

function onDatePickerCancel(evt, picker) {
	$(this).val('');
};

function addDatePicker(element, isSingle) {
	var config = getCalendarConfig(isSingle);
	element.daterangepicker(config);
	element.on('apply.daterangepicker', onDatePickerApply);
	element.on('cancel.daterangepicker', onDatePickerCancel);
};

function highlightElement(element) {
	element.css('border-color', 'red');
};

function unHighlightElement(element) {
	element.css('border-color', '');
};