$(document).ready(function() {
	$('#minsup').change(function(e) {
		$('#minsup-label').html('Soporte mínimo: <strong>' + $(this).val() + '</strong>')
	});
	$('#minconf').change(function(e) {
		$('#minconf-label').html('Confianza mínima: <strong>' + $(this).val() + '</strong>')
	});
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
				''
			);
		});
	});
});