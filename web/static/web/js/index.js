$(document).ready(function() {
	$('#form').submit(function(e) {
		e.preventDefault();
		$.ajax({
			url: 'ejecutar/',
			type: 'POST',
			data: new FormData( this ),
			processData: false,
			contentType: false
		}).done(function(data) {
			window.open(
				'popup/?task_id='+data['task_id']+'&filename='+data['filename']+'&minsup='+data['minsup']+'&minconf='+data['minconf'],
				'',
				"width=1000,height=600"
			);
		});
	});
});