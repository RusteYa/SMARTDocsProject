function add_delete_button(column) {
	column.append(
		$('<a>x</a>')
		.addClass('close')
		.on('click', function(evt) {
			$(evt.target).closest('tr').remove();
		})
	);
}

function create_new_textarea_column() {
	var $column = $('<td></td>');
	$column.append(
		$('<textarea></textarea>')
		.addClass('form-control')
	);
	return $column;
};

function create_new_date_column(date_range) {
	var $column = $('<td></td>');
	var $input = $('<input></input>').addClass('form-control');
	add_datepicker($input, date_range);
	$column.append($input);
	return $column;
};

function create_new_delete_column() {
	var $column = $('<td></td>');
	add_delete_button($column);
	return $column;
};

function create_new_row(date_range) {
	var $row = $('<tr></tr>');
	$row.append(create_new_textarea_column());
	$row.append(create_new_date_column(date_range));
	$row.append(create_new_delete_column());
	return $row;
};

function get_table_info() {
	var $table = $('#work-description-container');
	if ($table.length == 0) return false;
	return {
		date_range: $table.attr('multi-date') == 'true',
		body: $table.find('tbody'),
		rows: $table.find('tbody').find('tr')
	}
};

function get_row_info(row) {
	var $row = $(row);
	return {
		textarea: $row.find('textarea'),
		input: $row.find('input')
	}
};

function get_curator_info() {
	var $curator_info = $('#curator-info');
	if ($curator_info.length == 0) return false;
	return {
		fullname: $curator_info.find('input[name="curator-name"]'),
		position: $curator_info.find('input[name="curator-position"]')
	};
};

function _info_is_valid(row_info) {
	var valid = true;
	Object.keys(row_info).forEach(function(key) {
		if (row_info[key].val().length == 0) {
			valid = false;
			row_info[key].css('border-color', 'red');
		} else {
			row_info[key].css('border-color', '');
		}
	});
	return valid;
};

function table_info_is_valid(table_info) {
	var valid = table_info.rows.length != 0;
	console.log(table_info.rows.length);
	for (var i = 0; i < table_info.rows.length; i ++) {
		if (!_info_is_valid(get_row_info(table_info.rows[i]))) valid = false;
	}
	return valid;
};

function add_new_row() {
	var table_info = get_table_info();
	if (table_info.rows.length == 0 || table_info_is_valid(table_info)) {
		table_info.body.append(
			create_new_row(table_info.date_range)
		);
	} else {
		display_message('Пожалуйста, заполните все поля.', MESSAGES.WARNING);
	}
};

function send_document_to_server(json) {
	$.post({
		url: document.location,
		data: JSON.stringify(json),
		success: function(result, status, xhr) {
			if (result.message) {
				display_message(result.message, MESSAGES.WARNING);
			} else {
				display_message('Документ сохранён.', MESSAGES.SUCCESS);
			}
		}
	});
};

function save_doc() {
	var table_info = get_table_info();
	var curator_info = get_curator_info();
	var json = {works: [], curator_fio: '', curator_office: ''}; 
	var curator_valid = false;
	if (curator_info) {
		curator_valid = _info_is_valid(curator_info);
	} else {
		curator_valid = true;
	}
	json.curator_fio = '';
	json.curator_office = '';
	if (curator_info) {
		json.curator_fio = curator_info.fullname.val().trim();
		json.curator_office = curator_info.position.val().trim();
	}
	console.log(table_info);
	if (table_info) {
		if (table_info.rows.length == 0) {
			display_message('Вы не заполнили ни одного поля.', MESSAGES.WARNING);
			return;
		}
		if (table_info_is_valid(table_info) & curator_valid) {
			for (var i = 0; i < table_info.rows.length; i ++) {
				var row_info = get_row_info(table_info.rows[i]);
				json.works.push({
					num: i + 1,
					work: row_info.textarea.val().trim()
				});
				if (table_info.date_range) {
					var dates = row_info.input.val().split(' - ');
					json.works[i].start_date = dates[0];
					json.works[i].end_date = dates[1];
				} else {
					json.works[i].date = row_info.input.val();
				}
			}
			send_document_to_server(json);
		} else {
			display_message('Пожалуйста, заполните все поля.', MESSAGES.WARNING);
		}
	} else {
		send_document_to_server(json);
	}
};

function update_table_functions() {
	var table_info = get_table_info();
	if (table_info)
	for (var i = 0; i < table_info.rows.length; i ++) {
		var children = $(table_info.rows[i]).children();
		add_datepicker($(children[1]).children('input'), table_info.date_range);
		add_delete_button($(children[2]));
	}
};

$(function() {
	$('#add-new-row-btn').on('click', add_new_row);
	$('#save-doc-btn').on('click', save_doc);
	update_table_functions();
});