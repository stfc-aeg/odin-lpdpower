api_version = '0.1';

$( document ).ready(function() {

    update_api_version();
    update_api_adapters();

    get_led_states();

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

var cur_state = 0
function update_api_sensors()
{
    $.getJSON('/api/' + api_version + '/lpdpower/', function(response)
	{
		$('#api-temp').html(response.temp0.temperature);
		$('#api-button').html(response.output.input);
		$('#temp-label').html(response.temp0.temperature + "&deg;C");
		$('#progress-bar').attr("aria-valuenow", response.temp0.temperature);
		$('#progress-bar').css("width", (response.temp0.temperature * 2.5) + "%");

		if(response.temp0.flags.critical)
                {	
			if(cur_state != 0)
			{
                        	$("#progress-bar").attr("class", "progress-bar progress-bar-danger");
				cur_state = 0;
			}
                }
		else if(response.temp0.flags.high)
                {
			if(cur_state != 1)
			{
                        	$("#progress-bar").attr("class", "progress-bar progress-bar-warning");
				cur_state = 1;
			}
                }
		else if(response.temp0.flags.low)
                {	if(cur_state != 2)
			{
                        	$("#progress-bar").attr("class", "progress-bar progress-bar-info");
				cur_state = 2;
			}
                } 
                else if(cur_state != 3)
		{
			$("#progress-bar").attr("class", "progress-bar progress-bar-success");
			cur_state = 3;
		}
	});
}

var led_states = [false, false, false]

function get_led_states()
{
	$.getJSON('/api/' + api_version + '/lpdpower/output/outputs', function(response) {
        	led_states[0] = response.outputs["0"]
		led_states[1] = response.outputs["1"]
		led_states[2] = response.outputs["2"]

		$("#btn0").attr("class", led_states[0] ? "btn btn-success" : "btn btn-danger");
		$("#btn1").attr("class", led_states[1] ? "btn btn-success" : "btn btn-danger");
		$("#btn2").attr("class", led_states[2] ? "btn btn-success" : "btn btn-danger");

    	});

}

function apiButton(id)
{
	led_states[id] = !led_states[id]
	$("#btn" + id).attr("class", led_states[id] ? "btn btn-success" : "btn btn-danger");
	data = {}
	data[id] = led_states[id];
	$.ajax('/api/' + api_version + '/lpdpower/output/outputs',
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify(data)});
}
