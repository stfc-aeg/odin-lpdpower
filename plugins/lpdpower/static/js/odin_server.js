api_version = '0.1';

$( document ).ready(function() {

    update_api_version();
    update_api_adapters();

    setInterval(update_api_sensors, 200);
});

function update_api_version() {

    $.getJSON('/api', function(response) {
        $('#api-version').html(response.api_version);
        api_version = response.api_version;
    });
}

function update_api_adapters() {

    $.getJSON('/api/' + api_version + '/adapters/', function(response) {
        adapter_list = response.adapters.join(", ");
        $('#api-adapters').html(adapter_list);
    });
}

function update_api_sensors()
{
    $.getJSON('/api/' + api_version + '/lpdpower/', function(response)
	{
		$('#api-temp').html(response.temp0.temperature);
		$('#api-button').html(response.output.input);
	});
}

function apiButton(id)
{
	$.ajax('/api/' + api_version + '/lpdpower/output/outputs',
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({'0':id==1, '1':id==2, '2':id==3})});
}
