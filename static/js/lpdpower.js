//Global constants
const buttonOn = "btn-success";
const buttonOff = "btn-danger";
const colorOk = "#5cb85c";
const colorFail = "#d9534f";
const colorUnknown = '#555555';
const colorWarn = "#ffa500"

function round1dp(flt)
{
	//return Math.round(flt * 10) / 10;
    return flt.toFixed(1);
}

function round2dp(flt)
{
    return flt.toFixed(2);
}

function generateQuad(id)
{
	return `
<div class="caption">
	<div class="container-fluid">
		<div class="row"><h4>Quad ${id+1}:</h4></div>
		<div class="row">
			<div class="col-xs-5">Supply:</div>
			<div id="q${id}-sv" class="col-xs-5">&nbsp;</div>
		</div>
		<div class="row">
			<div class="col-xs-5">Trace:</div>
			<div id="q${id}-trace"  class="col-xs-5 status vertical-align">&nbsp;</div>
		</div>
	</div>
</div>
<table class="table table-striped">
	<thead>
		<tr>
			<th style="width:20%"></th>
			<th class="text-center" style="width:20%;">Channel A</th>
			<th class="text-center" style="width:20%;">Channel B</th>
			<th class="text-center" style="width:20%;">Channel C</th>
			<th class="text-center" style="width:20%;">Channel D</th>
		</tr>
	</thead>

	<tbody>
		<tr>
			<th scope="row">Voltage</th>
			<td><span id="q${id}-v0"></span>V</td>
			<td><span id="q${id}-v1"></span>V</td>
			<td><span id="q${id}-v2"></span>V</td>
			<td><span id="q${id}-v3"></span>V</td>
		</tr>

		<tr>
			<th scope="row">Fuse Voltage</th>
			<td><span id="q${id}-f0"></span>V</td>
			<td><span id="q${id}-f1"></span>V</td>
			<td><span id="q${id}-f2"></span>V</td>
			<td><span id="q${id}-f3"></span>V</td>
		</tr>

		<tr>
			<th scope="row">Current</th>
			<td><span id="q${id}-a0"></span>A</td>
			<td><span id="q${id}-a1"></span>A</td>
			<td><span id="q${id}-a2"></span>A</td>
			<td><span id="q${id}-a3"></span>A</td>
		</tr>

		<tr>
			<td></td>
			<td><button id="q${id}-btn0" type="button" class="btn btn-success" onclick="quadEnable(${id}, 0)">Disable</button></td>
			<td><button id="q${id}-btn1" type="button" class="btn btn-success" onclick="quadEnable(${id}, 1)">Disable</button></td>
			<td><button id="q${id}-btn2" type="button" class="btn btn-success" onclick="quadEnable(${id}, 2)">Disable</button></td>
			<td><button id="q${id}-btn3" type="button" class="btn btn-success" onclick="quadEnable(${id}, 3)">Disable</button></td>
		</tr>
	</tbody>
</table>
	`;
}

class Quad
{
	constructor(id)
	{
		this.map = new Map();
		this.enabled = [true,true,true,true] //Channel enabled states
		this.trace = false;
		var elements = document.querySelectorAll(`[id^='q${id}-']`);
		for (var i = 0; i < elements.length; ++i)
		{
			var start = 2 + id.toString().length;
			var key = elements[i].id.substr(start,
						elements[i].id.length - start);
			this.map.set(key, elements[i]);
		}
	}

	update(data)
	{
		//Update all the values in the table
		//Channel voltages
    	this.map.get("sv").innerHTML = round1dp(data.supply) + 'V';
		this.map.get("v0").innerHTML = round1dp(data.channels[0].voltage);
		this.map.get("v1").innerHTML = round1dp(data.channels[1].voltage);
		this.map.get("v2").innerHTML = round1dp(data.channels[2].voltage);
		this.map.get("v3").innerHTML = round1dp(data.channels[3].voltage);

		//Channel voltages after fuse
		this.map.get("f0").innerHTML = round1dp(data.channels[0].fusevoltage);
		this.map.get("f1").innerHTML = round1dp(data.channels[1].fusevoltage);
		this.map.get("f2").innerHTML = round1dp(data.channels[2].fusevoltage);
		this.map.get("f3").innerHTML = round1dp(data.channels[3].fusevoltage);

		//Channel currents
		this.map.get("a0").innerHTML = round1dp(data.channels[0].current);
		this.map.get("a1").innerHTML = round1dp(data.channels[1].current);
		this.map.get("a2").innerHTML = round1dp(data.channels[2].current);
		this.map.get("a3").innerHTML = round1dp(data.channels[3].current);

		for (var chan = 0; chan < 4; chan++)
		{
			var elem_name = "btn" + chan.toString();
			var el = this.map.get(elem_name);
			update_button_state(el, data.channels[chan].enabled, 'Disable', 'Enable')
			this.enabled[chan] = data.channels[chan].enabled
		}

	}

	updateTrace(value)
	{
		update_status_box(this.map.get('trace'), value, 'OK', 'Error')
	}
}

function generateTempSensors(count)
{
	var ret = `
<div class="caption">
	<div class="container-fluid">
		<div class="row"><h4>Temperature:</h4></div>
		<div class="row caption-row">
			<div class="col-xs-5">Status:</div>
			<div id="tmp-health" class="col-xs-5 status vertical-align">&nbsp;</div>
		</div>
		<div class="row caption-row">
			<div class="col-xs-5">Latched:</div>
			<div id="tmp-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
		</div>
	</div>
</div>
<table class="table table-striped">

	<thead>
		<tr>
			<th class="text-center" style="width:20%;">Sensor</th>
			<th class="text-center" style="width:25%;">Temp.</th>
			<th class="text-center" style="width:25%;">Set Point</th>
			<th class="text-center" style="width:10%;">Trace</th>
			<th class="text-center" style="width:10%;">Enable</th>
			<th class="text-center" style="width:10%;">Tripped</th>
		</tr>
	</thead>

	<tbody>
	`;

	for(id = 0; id < count; ++id)
	{
		ret += `
		<tr>
			<th class="text-center">Temp ${id+1}</th>
			<td><span id="tmp${id}-tmp"></span></td>
			<td><span id="tmp${id}-set"></span></td>
			<td><div id="tmp${id}-trace" class="status" ></div></td>
			<td><div id="tmp${id}-enable" class="status" ></div></td>
		    <td><div id="tmp${id}-trip" class="status"></div></td>
		</tr>
		`;
	}

	ret += "</tbody></table>";

	return ret;
}

class TempSensor
{
	constructor(id)
	{
		this.map = new Map();
		this.active = true;

		var elements = document.querySelectorAll(`[id^='tmp${id}-']`);
		for (var i = 0; i < elements.length; ++i)
		{
			var start = 4 + id.toString().length;
			var key = elements[i].id.substr(start,
						elements[i].id.length - start);
			this.map.set(key, elements[i]);
		}
	}

	update(data)
	{
	    this.map.get("trip").style.backgroundColor = data.tripped ? colorFail : colorOk;
	    this.map.get("trace").style.backgroundColor = data.trace ? colorOk : colorFail;
	    var temperatureVal = '';
	    var setpointVal = '';
	    if (data.disabled) {
		temperatureVal = 'N/C';
		setpointVal = 'N/C';
	    } else {
		temperatureVal = round1dp(data.temperature) + '°C';
		setpointVal = round1dp(data.setpoint) + '°C';
	    }
	    this.map.get("tmp").innerHTML = temperatureVal;
	    this.map.get("set").innerHTML = setpointVal;
	    this.map.get("enable").style.backgroundColor = data.disabled ? colorWarn : colorOk;
	}
}

function generateHumiditySensors(count)
{
	var ret = `
<div class="caption">
	<div class="container-fluid">
		<div class="row"><h4>Humidity:</h4></div>
		<div class="row caption-row">
			<div class="col-xs-5">Status:</div>
			<div id="h-health" class="col-xs-5 status vertical-align">&nbsp;</div>
		</div>
		<div class="row caption-row">
			<div class="col-xs-5">Latched:</div>
			<div id="h-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
		</div>
	</div>
</div>
<table class="table table-striped">

	<thead>
		<tr>
			<th class="text-center" style="width:20%;">Sensor</th>
			<th class="text-center" style="width:25%;">Humidity.</th>
			<th class="text-center" style="width:25%;">Set Point</th>
			<th class="text-center" style="width:10%;">Trace</th>
			<th class="text-center" style="width:10%;">Enable</th>
			<th class="text-center" style="width:10%;">Tripped</th>
		</tr>
	</thead>

	<tbody>
	`;

	for(id = 0; id < count; ++id)
	{
		ret += `
		<tr>
			<th class="text-center">Humid ${id+1}</th>
			<td><span id="h${id}-h"></span></td>
			<td><span id="h${id}-set"></span></td>
			<td><div id="h${id}-trace" class="status" ></div></td>
			<td><div id="h${id}-enable" class="status" ></div></td>
			<td><div id="h${id}-trip" class="status"></div></td>
		</tr>
		`;
	}

	ret += "</tbody></table>";

	return ret;
}

class HumiditySensor
{
	constructor(id)
	{
		this.map = new Map();
		this.active = true;

		var elements = document.querySelectorAll(`[id^='h${id}-']`);
		for (var i = 0; i < elements.length; ++i)
		{
			var start = 2 + id.toString().length;
			var key = elements[i].id.substr(start,
						elements[i].id.length - start);
			this.map.set(key, elements[i]);
		}
	}

	update(data)
	{
	    this.map.get("trip").style.backgroundColor = data.tripped ? colorFail : colorOk;
	    this.map.get("trace").style.backgroundColor = data.trace ? colorOk : colorFail;
	    var humidityValue = '';
	    var setpointValue = '';
	    if (data.disabled) {
		humidityValue = 'N/C';
		setpointValue = 'N/C'
	    } else {
		humidityValue = round1dp(data.humidity) + '%';
		setpointValue = round1dp(data.setpoint) + '%';
	    }
	    this.map.get("h").innerHTML = humidityValue;
	    this.map.get("set").innerHTML = setpointValue;
	    this.map.get("enable").style.backgroundColor = data.disabled ? colorWarn : colorOk;
	}
}

function generatePumpSensors(count)
{
	var ret = `
<div class="caption">
	<div class="container-fluid">
		<div class="row"><h4>Pump:</h4></div>
		<div class="row caption-row">
			<div class="col-xs-5">Status:</div>
			<div id="p-health" class="col-xs-5 status vertical-align">&nbsp;</div>
		</div>
		<div class="row caption-row">
			<div class="col-xs-5">Latched:</div>
			<div id="p-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
		</div>
	</div>
</div>
<table class="table table-striped">

	<thead>
		<tr>
			<th class="text-center" style="width:20%;">Sensor</th>
			<th class="text-center" style="width:25%;">Flow</th>
			<th class="text-center" style="width:25%;">Set Point</th>
			<th class="text-center" style="width:20%;"></th>
			<th class="text-center" style="width:10%;">Tripped</th>
		</tr>
	</thead>

	<tbody>
	`;

	for(id = 0; id < count; ++id)
	{
		ret += `
		<tr>
			<th class="text-center">Pump ${id+1}</th>
			<td><span id="p${id}-flow">0</span>l/min</td>
			<td><span id="p${id}-set">0</span>l/min</td>
			<td></td>
			<td><div id="p${id}-trip" class="status"></div></td>
		</tr>
		`;
	}

	ret += "</tbody></table>";

	return ret;
}

class PumpSensor
{
	constructor(id)
	{
		this.map = new Map();

		var elements = document.querySelectorAll(`[id^='p${id}-']`);
		for (var i = 0; i < elements.length; ++i)
		{
			var start = 2 + id.toString().length;
			var key = elements[i].id.substr(start,
						elements[i].id.length - start);
			this.map.set(key, elements[i]);
		}
	}

	update(data)
	{
		this.map.get("trip").style.backgroundColor = data.tripped ? colorFail : colorOk;
		this.map.get("flow").innerHTML = round1dp(data.flow);
		this.map.get("set").innerHTML = round1dp(data.setpoint);
	}
}

function generateFanSensors(count)
{
	var ret = `
<div class="caption">
	<div class="container-fluid">
	<div class="row"><h4>Fan:</h4></div>
	<div class="row caption-row">
		<div class="col-xs-5">Status:</div>
		<div id="f-health" class="col-xs-5 status vertical-align">&nbsp;</div>
	</div>
	<div class="row caption-row">
		<div class="col-xs-5">Latched:</div>
		<div id="f-latched"  class="col-xs-5 status vertical-align">&nbsp;</div>
	</div>
</div>
</div>
<table class="table table-striped">

	<thead>
		<tr>
			<th class="text-center" style="width:20%;">Sensor</th>
			<th class="text-center" style="width:20%;">Current Speed</th>
			<th class="text-center" style="width:20%;">Set Point</th>
			<!-- <th class="text-center" style="width:14%;">Potentiometer</th> -->
			<th class="text-center" style="width:30%;">Target Speed</th>
			<th class="text-center" style="width:10%;">Tripped</th>
		</tr>
	</thead>

	<tbody>
	`;

	for(id = 0; id < count; ++id)
	{
		ret += `
		<tr>
			<th class="text-center">Fan ${id+1}</th>
			<td><span id="f${id}-speed">0</span>Hz</td>
			<td><span id="f${id}-set">0</span>Hz</td>
			<!-- <td><span id="f${id}-pot">0</span>%</td> -->
			<td>
				<div class="input-group">
					<input class="form-control" type="text" id="f${id}-target" aria-label="Target fan speed (Hz)">
					<span class="input-group-addon">%</span>
					<span class="input-group-btn">
					        <button class="btn btn-default" type="button" onclick="updateSpeed(${id})">Set</button>
				        </span>
				</div>
			</td>
			<td><div id="f${id}-trip" class="status"></div></td>
		</tr>
		`;
	}

	ret += "</tbody></table>";

	return ret;
}

class FanSensor
{
	constructor(id)
	{
		this.map = new Map();
		this.target = 0.0;

		var elements = document.querySelectorAll(`[id^='f${id}-']`);
		for (var i = 0; i < elements.length; ++i)
		{
			var start = 2 + id.toString().length;
			var key = elements[i].id.substr(start,
						elements[i].id.length - start);
			this.map.set(key, elements[i]);
		}
	}

	update(data)
	{
		this.map.get("trip").style.backgroundColor = data.tripped ? colorFail : colorOk;
		this.map.get("speed").innerHTML = round1dp(data.currentspeed);
		//this.map.get("pot").innerHTML = round1dp(data.potentiometer);
    	this.map.get("set").innerHTML = round1dp(data.setpoint);

		if(data.target != this.target)
		{
			this.map.get("target").placeholder = data.target.toString();
			this.target = data.target;
		}
	}
}

//Add templates to page
var lpdpower_html = "";
lpdpower_html += generateQuad(0);
lpdpower_html += generateQuad(1);
lpdpower_html += generateQuad(2);
lpdpower_html += generateQuad(3);
lpdpower_html += generateTempSensors(11);
lpdpower_html += generateHumiditySensors(2);
lpdpower_html += generatePumpSensors(1);
lpdpower_html += generateFanSensors(1);
$("#lpdpower").html(lpdpower_html);

var quads = [];
var temp_sensors = [];
var humidity_sensors = [];
var pump_sensor;
var fan_sensor;

var global_elems = new Map();
$(document).ready(function()
{
	//Get sensors and cache DOM elements
	for(var i = 0; i < 4; ++i)
		quads.push(new Quad(i));
	for(var i = 0; i < 11; ++i)
		temp_sensors.push(new TempSensor(i));
	for(var i = 0; i < 2; ++i)
		humidity_sensors.push(new HumiditySensor(i));

	pump_sensor = new PumpSensor(0);
	fan_sensor = new FanSensor(0);

	var elems = document.querySelectorAll("[id$='-health']");
	for(var i = 0; i < elems.length; ++i)
		global_elems.set(elems[i].id, elems[i]);

    var latched_elems = document.querySelectorAll("[id$='-latched']");
    for(var i = 0; i < latched_elems.length; i++)
        global_elems.set(latched_elems[i].id, latched_elems[i]);

	global_elems.set("overall-status", document.querySelector("#overall-status"));
	global_elems.set("overall-latched", document.querySelector("#overall-latched"));
	global_elems.set("overall-armed", document.querySelector("#overall-armed"));
	global_elems.set("trace-status", document.querySelector("#trace-status"));
    global_elems.set("trace-latched", document.querySelector("#trace-latched"));
    global_elems.set("position", document.querySelector("#position"));
	global_elems.set("arm", document.querySelector("#button-arm"));
	global_elems.set("enable", document.querySelector("#button-enable"));

	//Start update function
	setInterval(updateAll, 200);
});

function update_status_box(el, value, text_true, text_false)
{
	el.style.backgroundColor = value ? colorOk : colorFail;
	el.innerHTML = value ? text_true : text_false;
}

function update_button_state(el, value, text_true, text_false)
{
	el.classList.add(value ? buttonOn : buttonOff);
	el.classList.remove(value ? buttonOff: buttonOn);
	el.innerHTML = value ? text_true : text_false;
}

function updateAll()
{
	$.getJSON('/api/0.1/lpdpower/', function(response)
	{
		//Handle quads
		for(var i = 0; i < quads.length; ++i)
		{
			quads[i].update(response.quad.quads[i]);
			quads[i].updateTrace(response.quad.trace[i]);
		}

		//Handle temp sensors
		for(var i = 0; i < temp_sensors.length; ++i)
			temp_sensors[i].update(response.temperature.sensors[i]);

		//Handle humidity sensors
		for(var i = 0; i < humidity_sensors.length; ++i)
			humidity_sensors[i].update(response.humidity.sensors[i]);

		//Handle pump sensor
		pump_sensor.update(response.pump);

		//Handle fan sensor
		fan_sensor.update(response.fan);

		//Handle overall status

		update_status_box(global_elems.get("overall-status"), response.overall, 'Healthy', 'Error')
		update_status_box(global_elems.get("overall-latched"), response.latched, 'No', 'Yes')
		update_status_box(global_elems.get("overall-armed"), response.armed, 'Yes', 'No')
		update_status_box(global_elems.get("trace-status"), response.trace.overall, 'OK', 'Error')
		update_status_box(global_elems.get("trace-latched"), response.trace.latched, 'No', 'Yes')
		global_elems.get("position").innerHTML = round2dp(response.position).toString() + 'mm'

		// Handle health states
		update_status_box(global_elems.get("tmp-health"), response.temperature.overall, 'Healthy', 'Error');
		update_status_box(global_elems.get("h-health"), response.humidity.overall, 'Healthy', 'Error');
		update_status_box(global_elems.get("p-health"), response.pump.overall, 'Healthy', 'Error');
		update_status_box(global_elems.get("f-health"), response.fan.overall, 'Healthy', 'Error');

	    // Handle latched states
		update_status_box(global_elems.get("tmp-latched"), response.temperature.latched, 'No', 'Yes')
		update_status_box(global_elems.get("h-latched"), response.humidity.latched, 'No', 'Yes')
		update_status_box(global_elems.get("p-latched"), response.pump.latched, 'No', 'Yes')
		update_status_box(global_elems.get("f-latched"), response.fan.latched, 'No', 'Yes')

        // Handle button states
        update_button_state(global_elems.get("arm"), response.armed, 'Disarm Interlock', 'Arm Interlock');
        update_button_state(global_elems.get("enable"), response.allEnabled, 'Disable Quads', 'Enable Quads');

	});
}

function quadEnable(qid, bid)
{
	$.ajax(`/api/0.1/lpdpower/quad/quads/${qid}/channels/${bid}`,
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({enabled: !quads[qid].enabled[bid]})});
}

function tmpEnable(tmpid)
{
	$.ajax(`/api/0.1/lpdpower/temperature/sensors/${tmpid}`,
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({disable: temp_sensors[tmpid].active})});
}

function humidityEnable(hid)
{
	$.ajax(`/api/0.1/lpdpower/humidity/sensors/${hid}`,
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({disable: humidity_sensors[hid].active})});
}

function armInterlock()
{
    $.ajax('/api/0.1/lpdpower/',
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({armed: global_elems.get("arm").classList.contains(buttonOff)})});
}

function enableQuads()
{
    $.ajax('/api/0.1/lpdpower/',
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({allEnabled: global_elems.get("enable").classList.contains(buttonOff)})});
}

function updateSpeed(fid)
{
    var el = fan_sensor.map.get("target");
    var value = parseFloat(el.value);
    if(isNaN(value))
	{
	    alert("The fan speed must be a decimal number!");
	    return;
	}
    el.value = "";

    $.ajax('/api/0.1/lpdpower/fan',
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({target: value})});
}
