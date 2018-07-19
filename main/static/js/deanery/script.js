function deleteClosedDocumentsRows(documents) {
	var documentLists = $('table[name="document-list"]');
	documentLists.find('tbody').children().each(function() {
		if (documents.includes(parseInt($(this).find('input[name="document-id"]').val()))) {
			$(this).remove();
		}
	});
	documentLists.find('tbody').each(function() {
		if ($(this).children().length == 0) {
			$(this).closest('div.card').remove();
		}
	});
};

function sendData(status) {
	json = {
		document_ids: getChoosenRowsDocumentIDs(),
		status: status
	};
	if (json.document_ids.length == 0) {
		displayMessage('Вы ничего не выбрали.', MESSAGES.WARNING);
		return;
	}
	$.post({
		url: '/app/deanery/document/change_status/',
		data: JSON.stringify(json),
		success: function(result, status, xhr) {
			if (result.message) {
				displayMessage(result.message, MESSAGES.WARNING);
			} else {
				displayMessage('Успешно.', MESSAGES.SUCCESS);
				deleteClosedDocumentsRows(json.document_ids);
			}
		}
	});
};

function acceptDocuments() {
	sendData(1);
};

function declineDocuments() {
	sendData(2);
};

function getChoosenRowsDocumentIDs() {
	var documentLists = $('table[name="document-list"]');
	var choosenIDs = [];
	documentLists.find('tbody').children().each(function() {
		if ($(this).is(':visible') && $(this).find('input[name="choosen"]').is(':checked'))
			choosenIDs.push(parseInt($(this).find('input[name="document-id"]').val()));
	});
	return choosenIDs;
};

function hidePracticeIfNoSuchDocuments() {
	var cards = $('div.card');
	cards.each(function() {
		var trs = $(this).find('tr');
		var k = trs.length;
		trs.each(function() {
			if (!$(this).is(':visible')) k --;
		});
		if (k == 1) {$(this).hide();} else {$(this).show();}
	});
};

function filterDocumentsByType(evt) {
	var select = $(evt.target);
	var documentLists = $('table[name="document-list"]');
	documentLists.find('tbody').children().each(function() {
		if ($(this).find('input[name="document-type"]').val() != select.val() && select.val() != '-1') {
			$(this).hide();
		} else {
			$(this).show();
		}
	});
	hidePracticeIfNoSuchDocuments();
};

function filterDocumentsByPractice(evt) {
	var select = $(evt.target);
	var documentLists = $('table[name="document-list"]');
	documentLists.each(function() {
		var header = $(this).closest('div.card-body').prev();
		if (header.find('input[name="practice-id"]').val() != select.val() && select.val() != '-1') {
			header.closest('div.card').hide();
		} else {
			header.closest('div.card').show();
		}
	});
};

$(function() {
	$('#accept-doc-btn').on('click', acceptDocuments);
	$('#decline-doc-btn').on('click', declineDocuments);
	$('#deanery-documents-type').on('change', filterDocumentsByType);
	$('#deanery-practice').on('change', filterDocumentsByPractice);
});