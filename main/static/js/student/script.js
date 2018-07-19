function deleteTableRow(evt) {
	$(evt.target).closest('tr').remove();
};

function createPracticeDiaryTextareaColumn() {
	var td = createElement('td');
	var textarea = createElement('textarea');
	textarea.addClass('md-textarea form-control');
	td.append(textarea);
	return td;
};

function createPracticeDiaryDateInputColumn() {
	var td = createElement('td');
	var input = createElement('input');
	input.addClass('md-textarea form-control');
	addDatePicker(input, true);
	td.append(input);
	return td;
};

function createPracticeDiaryActionColumn() {
	var td = createElement('td');
	td.addClass('text-center');
	var a = createElement('a');
	a.on('click', deleteTableRow);
	a.text('Удалить');
	td.append(a);
	return td;
};

function createPracticeDiaryRow() {
	var row = createElement('tr');
	row.append(createPracticeDiaryTextareaColumn());
	row.append(createPracticeDiaryDateInputColumn());
	row.append(createPracticeDiaryActionColumn());
	return row;
};

function createIndividualTaskDateInputColumn() {
	var td = createElement('td');
	var input = createElement('input');
	input.addClass('form-control');
	addDatePicker(input, false);
	td.append(input);
	return td;
};

function createIndividualTaskRow() {
	var row = createElement('tr');
	row.append(createPracticeDiaryTextareaColumn());
	row.append(createIndividualTaskDateInputColumn());
	row.append(createPracticeDiaryActionColumn());
	return row;
};

function tableHasDateRange(table) {
	return table.attr('date-range') == 'true';
};

function tableHasNoChildren(table) {
	return table.find('tbody').children().length == 0;
};

function tableHasNoEmptyFields(table) {
	var notEmpty = true;
	var tbody = table.find('tbody');
	tbody.children().each(function() {
		var textarea = $(this).find('textarea');
		var input = $(this).find('input');
		if (textarea.val().trim().length == 0) {
			notEmpty = false;
			highlightElement(textarea);
		} else {
			unHighlightElement(textarea);
		}
		if (input.val().trim().length == 0) {
			notEmpty = false;
			highlightElement(input);
		} else {
			unHighlightElement(input);
		}
	});
	return notEmpty;
};

function tableIsValid(table) {
	var valid = true;
	var tbody = table.find('tbody');
	tbody.children().each(function() {
		var input = $(this).find('input');
		if (!input.val().match(/\d{2}.\d{2}.\d{4}/)) {
			valid = false;
			highlightElement(input);
		} else {
			unHighlightElement(input);
		}
	});
	return valid;
};

function addRowToTable() {
	var table = $('#student-practice-table');
	var tbody = table.find('tbody');
	if (tableHasNoChildren(table) || (tableHasNoEmptyFields(table) && tableIsValid(table))) {
		var row = null;
		if (tableHasDateRange(table)) {
			row = createIndividualTaskRow();
		} else {
			row = createPracticeDiaryRow();
		}
		tbody.append(row);
	} else {
		displayMessage('Пожалуйста, заполните все поля.', MESSAGES.WARNING);
	}
};

function curatorInfoHasNoEmptyFields(curatorInfo) {
	var notEmpty = true;
	curatorInfo.find('input').each(function() {
		if ($(this).val().trim().length == 0) {
			notEmpty = false;
			highlightElement($(this));
		} else {
			unHighlightElement($(this));
		}
	});
	return notEmpty;
};

function getCuratorInfo() {
	var curatorInfo = $('#student-practice-curator-info');
	if (curatorInfo.length == 0) return false;
	var info = {
		firstName: curatorInfo.find('input[name="student-practice-curator-first-name"]').val().trim(),
		secondName: curatorInfo.find('input[name="student-practice-curator-second-name"]').val().trim(),
		middleName: curatorInfo.find('input[name="student-practice-curator-middle-name"]').val().trim(),
		position: curatorInfo.find('input[name="student-practice-curator-position"]').val().trim()
	};
	return info;
};

function sendData(json) {
	$.post({
		url: document.location,
		data: JSON.stringify(json),
		success: function(result, status, xhr) {
			if (result.message) {
				displayMessage(result.message, MESSAGES.WARNING);
			} else {
				displayMessage('Документ сохранён.', MESSAGES.SUCCESS);
			}
		}
	});
};

function saveDocument() {
	var table = $('#student-practice-table');
	var tbody = table.find('tbody');
	var json = {works: [], curator_fio: '', curator_office: ''};
	var curatorInfo = getCuratorInfo();
	var curatorInfoValid = true;
	if (curatorInfo) {
		curatorInfoValid = curatorInfoHasNoEmptyFields($('#student-practice-curator-info'));
		json.curator_fio = [curatorInfo.secondName, curatorInfo.firstName, curatorInfo.middleName].join(' ');
		json.curator_office = curatorInfo.position;
	}
	if (table.length != 0) {
		if (tableHasNoChildren(table)) {
			displayMessage('Вы не заполнили ни одного поля.', MESSAGES.WARNING);
			return;
		}
		if (tableHasNoEmptyFields(table) && tableIsValid(table) && curatorInfoValid) {
			var k = 1;
			tbody.children().each(function() {
				var textarea = $(this).find('textarea');
				var input = $(this).find('input');
				json.works.push({
					num: k,
					work: textarea.val().trim()
				});
				var dates = input.val().split(' - ');
				if (dates.length == 2) {
					json.works[k-1].start_date = dates[0];
					json.works[k-1].end_date = dates[1];
				} else {
					json.works[k-1].date = dates[0];
				}
				k ++;
			});
			sendData(json);
		} else {
			displayMessage('Пожалуйста, заполните все поля.', MESSAGES.WARNING);
		}
	} else {
		sendData(json);
	}
};

function updateTable() {
	var table = $('#student-practice-table');
	if (table.length != 0) {
		var tbody = table.find('tbody');
		tbody.children().each(function() {
			addDatePicker($(this).find('input'), !tableHasDateRange(table));
			$(this).append(createPracticeDiaryActionColumn());
		});
	}
};

$(function() {
	$('#add-new-row-btn').on('click', addRowToTable);
	$('#save-doc-btn').on('click', saveDocument);
	updateTable();
});