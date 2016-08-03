//Global constants
const buttonOn = "btn-success";
const buttonOff = "btn-danger";
const colorOk = "#5cb85c";
const colorFail = "#d9534f";

function round1dp(flt)
{
	//return Math.round(flt * 10) / 10;
    return flt.toFixed(1);
}

function enableButton(el)
{
	el.classList.remove(buttonOff);
	el.classList.add(buttonOn);
	el.innerHTML = "Disable";
}

function disableButton(el)
{
	el.classList.remove(buttonOn);
	el.classList.add(buttonOff);
	el.innerHTML = "Enable";
}

function generateQuad(id)
{
	return `
<div class="caption">
	<h3>Quad ${id+1}:</h3>
	<p>Supply Voltage: <span id="q${id}-sv"></span>V</p>
	<p class="error" id="q${id}-trace">Quad ${id+1} was not detected!</p>
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
		this.map.get("sv").innerHTML = data.supply;
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

		var el = this.map.get("btn0");
		if(data.channels[0].feedback && !this.enabled[0])
		{
			enableButton(el);
			this.enabled[0] = data.channels[0].feedback;
		}
		else if(!data.channels[0].feedback && this.enabled[0])
		{
			disableButton(el);
			this.enabled[0] = data.channels[0].feedback;
		}
		
		el = this.map.get("btn1");
		if(data.channels[1].feedback && !this.enabled[1])
		{
			enableButton(el);
			this.enabled[1] = data.channels[1].feedback;
		}
		else if(!data.channels[1].feedback && this.enabled[1])
		{
			disableButton(el);
			this.enabled[1] = data.channels[1].feedback;
		}

		el = this.map.get("btn2");
		if(data.channels[2].feedback && !this.enabled[2])
		{
			enableButton(el);
			this.enabled[2] = data.channels[2].feedback;
		}
		else if(!data.channels[2].feedback && this.enabled[2])
		{
			disableButton(el);
			this.enabled[2] = data.channels[2].feedback;
		}

		el = this.map.get("btn3");
		if(data.channels[3].feedback && !this.enabled[3])
		{
			enableButton(el);
			this.enabled[3] = data.channels[3].feedback;
		}
		else if(!data.channels[3].feedback && this.enabled[3])
		{
			disableButton(el);
			this.enabled[3] = data.channels[3].feedback;
		}
	}

	updateTrace(value)
	{
		if(this.trace != value)
		{
			this.trace = value;
			if(value)
				this.map.get("trace").classList.add("hidden");
			else
				this.map.get("trace").classList.remove("hidden");
		}
	}
}

function generateTempSensors(count)
{
	var ret = `
<div class="caption">
	<h3>Temperature:</h3>
	<div class="status" id="tmp-health">Status</div>
	<div class="status" id="tmp-latched">Latched</div>
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
			<td><span id="tmp${id}-tmp"></span>°C</td>
			<td><span id="tmp${id}-set"></span>°C</td>
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
		this.map.get("tmp").innerHTML = round1dp(data.temperature);
		this.map.get("set").innerHTML = round1dp(data.setpoint);
		this.map.get("enable").style.backgroundColor = data.disabled ? colorFail : colorOk;
	}
}

function generateHumiditySensors(count)
{
	var ret = `
<div class="caption">
	<h3>Humidity:</h3>
	<div class="status" id="h-health">Status</div>
	<div class="status" id="h-latched">Latched</div>
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
			<td><span id="h${id}-h"></span>%</td>
			<td><span id="h${id}-set"></span>%</td>
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
		this.map.get("h").innerHTML = round1dp(data.humidity);
		this.map.get("set").innerHTML = round1dp(data.setpoint);
		this.map.get("enable").style.backgroundColor = data.disabled ? colorFail : colorOk;
	}
}

function generatePumpSensors(count)
{
	var ret = `
<div class="caption">
	<h3>Pump:</h3>
	<div class="status" id="p-health">Status</div>
	<div class="status" id="p-latched">Latched</div>
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
	<h3>Fan:</h3>
	<div class="status" id="f-health">Status</div>
	<div class="status" id="f-latched">Latched</div>
</div>
<table class="table table-striped">

	<thead>
		<tr>
			<th class="text-center" style="width:20%;">Sensor</th>
			<th class="text-center" style="width:14%;">Current Speed</th>
			<th class="text-center" style="width:13%;">Set Point</th>
			<th class="text-center" style="width:14%;">Potentiometer</th>
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
			<td><span id="f${id}-pot">0</span>%</td>
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
		this.map.get("pot").innerHTML = round1dp(data.potentiometer);
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

var armed = true;

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
	global_elems.set("trace-status", document.querySelector("#trace-status"));
        global_elems.set("trace-latched", document.querySelector("#trace-latched"));
	global_elems.set("enable", document.querySelector("#overall-enable"));
	global_elems.set("arm", document.querySelector("#overall-arm"));

	//Start update function
	setInterval(updateAll, 200);
});

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

		//Handle overall health
		global_elems.get("tmp-health").style.backgroundColor = response.temperature.overall ? colorOk : colorFail;
		global_elems.get("h-health").style.backgroundColor = response.humidity.overall ? colorOk : colorFail;
		global_elems.get("p-health").style.backgroundColor = response.pump.overall ? colorOk : colorFail;
		global_elems.get("f-health").style.backgroundColor = response.fan.overall ? colorOk : colorFail;
		global_elems.get("overall-status").style.backgroundColor = response.overall ? colorOk : colorFail;
		global_elems.get("trace-status").style.backgroundColor = response.trace.overall ? colorOk : colorFail;

	        // Handler latched states
                global_elems.get("tmp-latched").style.backgroundColor = response.temperature.latched ? colorOk: colorFail;
                global_elems.get("trace-latched").style.backgroundColor = response.trace.latched ? colorOk: colorFail;
                global_elems.get("h-latched").style.backgroundColor = response.humidity.latched ? colorOk: colorFail;
                global_elems.get("f-latched").style.backgroundColor = response.fan.latched ? colorOk: colorFail;
                global_elems.get("p-latched").style.backgroundColor = response.pump.latched ? colorOk: colorFail;

		if(response.isarmed && !armed)
		{
			var el = global_elems.get("arm");
			el.classList.add(buttonOn);
			el.classList.remove(buttonOff);
			el.innerHTML = "Disarm Interlock";
			armed = true;
		}
		else if(!response.isarmed && armed)
		{
			var el = global_elems.get("arm");
			el.classList.add(buttonOff);
			el.classList.remove(buttonOn);
			el.innerHTML = "Arm Interlock";
			armed = false;
		}
	});
}

function quadEnable(qid, bid)
{
	$.ajax(`/api/0.1/lpdpower/quad/quads/${qid}/channels/${bid}`,
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({enable: !quads[qid].enabled[bid]})});
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
		data: JSON.stringify({arm: global_elems.get("arm").classList.contains(buttonOff)})});
}

function enableQuads()
{
    $.ajax('/api/0.1/lpdpower/',
		{method: 'PUT',
		contentType: 'application/json',
		processData: false,
		data: JSON.stringify({enableall: true})});
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

