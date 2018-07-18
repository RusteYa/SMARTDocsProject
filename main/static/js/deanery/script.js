function set_group_list(data) {
	var $select = $('select[name="connection_choices]"');
	console.log(data);
};

function set_practice_list(data) {
	var $select = $('select[name="connection_choices]"');
	console.log(data);
};

function request_group_list() {
	$.get({
		url: '/app/deanery/groups/',
		success: function(result, status, xhr) {
			set_group_list(result);
		}
	});
};

function request_practice_list() {
	$.get({
		url: '/app/deanery/practices/',
		success: function(result, status, xhr) {
			set_practice_list(result);
		}
	});
};

function change_connection_type(evt) {
	var select = evt.target;
	if (select.value == 'group') {
		request_group_list();
	} else if (select.value == 'practice') {
		request_practice_list();
	}
};

function filter_students_by(rows, by, filter) {
	var hide = false;
	rows.each(function() {
		if (typeof filter == 'string') {
			if (!$(this).find('td[name="student_' + by + '"]').val().match(/filter/)) {
				hide = true;
			}
		} else if (typeof filter == 'number') {
			if (parseInt($(this).find('td[name="student_' + by + '"]').val()) != filter) {
				hide = true;
			}
		}
		if (hide) {
			$(this).css('display', 'none');
		} else {
			$(this).css('display', '');
		}
	});
};

function get_choosen_students() {
	var $table = $('#student-list');
	var $tbody = $table.find('tbody');
	var students = [];
	$tbody.children().each(function() {
		students.push(parseInt($(this).find('input[name="student_id]"').val()));
	});
	console.log(students);
	return students;
};

function get_practice_info() {
	var $practice = $('#practice-form');
	return {
		id: $practice.find('select[name="practice-id"]'),
		name: $practice.find('input[name="practice-name"]'),
		type: $practice.find('select[name="practice-type"]'),
		curator: $practice.find('select[name="practice-curator"]'),
		date: $practice.find('input[name="practice-date"]'),
		address: $practice.find('input[name="practice-address"]'),
		institute: $practice.find('input[name="practice-institute"]'),
		specialization: $practice.find('input[name="practice-specialization"]')
	};
};

function practice_info_is_valid(practice_info) {
	var valid = true;
	Object.keys(practice_info).forEach(function(key) {
		if (practice_info[key].val().length == 0) {
			valid = false;
			practice_info[key].css('border-color', 'red');
		} else {
			practice_info[key].css('border-color', '');
		}
	});
	return valid;
};

function send_practice_to_server(json) {
	$.post({
		url: document.location,
		data: JSON.stringify(json),
		success: function(result, status, xhr) {
			if (result.message) {
				display_message(result.message, MESSAGES.WARNING);
			} else {
				display_message('Сохранено.', MESSAGES.SUCCESS);
			}
		}
	});
};

function clear_practice_data(practice_info) {
	Object.keys(practice_info).forEach(function(key) {
		practice_info[key].val('');
	});
	practice_info.id.val(practice_info.id.children().first().val());
	practice_info.curator.val(practice_info.curator.children().first().val());
	practice_info.type.val(practice_info.type.children().first().val());
};

function request_practice_delete(practice_info) {
	$.get({
		url: '/app/deanery/practice/delete/' + practice_info.id.val() + '/',
		success: function(result, status, xhr) {
			if (result.message) {
				display_message(result.message, MESSAGES.WARNING);
			} else {
				display_message('Успешно удалено.', MESSAGES.SUCCESS);
			}
			clear_practice_data(practice_info);
		}
	});
};

function delete_practice() {
	var practice_info = get_practice_info();
	if (practice_info.id.val() != '-1') {
		request_practice_delete(practice_info);
	} else {
		display_message('Выберите практику для удаления.', MESSAGES.WARNING);
	}
};

function save_practice() {
	var practice_info = get_practice_info();
	var json = {};
	if (practice_info_is_valid(practice_info)) {
		json = {
			name: practice_info.name.val(),
			type_of: practice_info.type.val(),
			curator: practice_info.curator.val(),
			address: practice_info.address.val(),
			institute: practice_info.institute.val(),
			speciality: practice_info.specialization.val(),
		}
		var dates = practice_info.date.val().split(' - ');
		json.start_date = dates[0];
		json.end_date = dates[1];
		if (practice_info.id.val() != '-1') {
			json.practice_id = parseInt(practice_info.id.val());
		}
		send_practice_to_server(json);
	} else {
		display_message('Пожалуйста, заполните все поля.', MESSAGES.WARNING);
	}
};

function set_practice_data(practice_info, data) {
	practice_info.name.val(data.name);
	practice_info.type.val(data.type_of);
	practice_info.curator.val(data.curator);
	practice_info.address.val(data.address);
	practice_info.institute.val(data.institute);
	practice_info.specialization.val(data.speciality);
	practice_info.date.val(data.start_date + ' - ' + data.end_date);
};

function request_practice(practice_info) {
	$.get({
		url: '/app/deanery/practice/get/' + practice_info.id.val() + '/',
		success: function(result, status, xhr) {
			set_practice_data(practice_info, result.practice);
		}
	});
};

function load_practice_data() {
	var practice_info = get_practice_info();
	$title = $('#page-title');
	if (practice_info.id.val() == '-1') {
		$title.text('Создать');
		clear_practice_data(practice_info);
	} else {
		request_practice(practice_info);
		$title.text('Редактировать');
	}
};

$(function() {
	$('select[name="connection_choices"]').on('change', change_connection_type);
	$('#save-practice-btn').on('click', save_practice);
	$('#delete-practice-btn').on('click', delete_practice);
	$('select[name="practice-id"]').on('change', load_practice_data);
	add_datepicker($('input[name="practice-date"]'), true);
});