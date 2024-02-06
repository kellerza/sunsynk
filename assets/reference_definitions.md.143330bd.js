import{_ as s,o as a,c as n,Q as e}from"./chunks/framework.dfcac6be.js";const F=JSON.parse('{"title":"Sensors","description":"","frontmatter":{},"headers":[],"relativePath":"reference/definitions.md","filePath":"reference/definitions.md","lastUpdated":1707245027000}'),p={name:"reference/definitions.md"},l=e(`<h1 id="sensors" tabindex="-1">Sensors <a class="header-anchor" href="#sensors" aria-label="Permalink to &quot;Sensors&quot;">​</a></h1><p>You can add sensors under the <code>SENSORS</code> and <code>SENSORS_FIRST_INVERTER</code> keys in the configuration.</p><p>If you want to add the <em>Battery SOC</em> sensor, you can use any of the following formats. In the logs you will see the first format (no spaces and all lower case).</p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSORS</span><span style="color:#E1E4E8;">:</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">battery_soc</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">Battery SOC</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">battery_SOC</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSORS</span><span style="color:#24292E;">:</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">battery_soc</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">Battery SOC</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">battery_SOC</span></span></code></pre></div><p>This page lists common sensors that can also be added through sensor groups. You can find all the supported sensor names in the sensor definition files, or even use the Modbus protocol document to create your own definitions.</p><h2 id="sensor-definitions" tabindex="-1">Sensor definitions <a class="header-anchor" href="#sensor-definitions" aria-label="Permalink to &quot;Sensor definitions&quot;">​</a></h2><p>The sensor definitions include the modbus register number (or several registers), the name of the sensor, the unit and other optional parameters. For example:</p><div class="language-python vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">python</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#E1E4E8;">Sensor(</span><span style="color:#79B8FF;">183</span><span style="color:#E1E4E8;">, </span><span style="color:#9ECBFF;">&quot;Battery voltage&quot;</span><span style="color:#E1E4E8;">, </span><span style="color:#79B8FF;">VOLT</span><span style="color:#E1E4E8;">, </span><span style="color:#79B8FF;">0.01</span><span style="color:#E1E4E8;">),</span></span>
<span class="line"><span style="color:#E1E4E8;">Sensor(</span><span style="color:#79B8FF;">184</span><span style="color:#E1E4E8;">, </span><span style="color:#9ECBFF;">&quot;Battery SOC&quot;</span><span style="color:#E1E4E8;">, </span><span style="color:#9ECBFF;">&quot;%&quot;</span><span style="color:#E1E4E8;">),</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#24292E;">Sensor(</span><span style="color:#005CC5;">183</span><span style="color:#24292E;">, </span><span style="color:#032F62;">&quot;Battery voltage&quot;</span><span style="color:#24292E;">, </span><span style="color:#005CC5;">VOLT</span><span style="color:#24292E;">, </span><span style="color:#005CC5;">0.01</span><span style="color:#24292E;">),</span></span>
<span class="line"><span style="color:#24292E;">Sensor(</span><span style="color:#005CC5;">184</span><span style="color:#24292E;">, </span><span style="color:#032F62;">&quot;Battery SOC&quot;</span><span style="color:#24292E;">, </span><span style="color:#032F62;">&quot;%&quot;</span><span style="color:#24292E;">),</span></span></code></pre></div><p>The last parameter in the battery voltage sensor definition is a factor, in this case a value of 1 in the register represents 0.01V. When the factor is negative for normal sensors it indicates that the number in the register is Signed (it can be negative &amp; positive)</p><p>To enable both these sensors in your configuration, simply use the names:</p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSORS</span><span style="color:#E1E4E8;">:</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">battery_voltage</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">battery_soc</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSORS</span><span style="color:#24292E;">:</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">battery_voltage</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">battery_soc</span></span></code></pre></div><h2 id="single-phase-inverter-sensor-definitions" tabindex="-1">Single Phase Inverter Sensor Definitions <a class="header-anchor" href="#single-phase-inverter-sensor-definitions" aria-label="Permalink to &quot;Single Phase Inverter Sensor Definitions&quot;">​</a></h2><p>You can find all the definitions here: <a href="https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions.py" target="_blank" rel="noreferrer">https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions.py</a></p><p>These definitions are used when you configure a single-phase inverter in the addon:</p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSOR_DEFINITIONS</span><span style="color:#E1E4E8;">: </span><span style="color:#9ECBFF;">single-phase</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSOR_DEFINITIONS</span><span style="color:#24292E;">: </span><span style="color:#032F62;">single-phase</span></span></code></pre></div><h2 id="three-phase-inverter-sensor-definitions" tabindex="-1">Three Phase Inverter Sensor Definitions <a class="header-anchor" href="#three-phase-inverter-sensor-definitions" aria-label="Permalink to &quot;Three Phase Inverter Sensor Definitions&quot;">​</a></h2><p>You can find all the definitions here: <a href="https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions3ph.py" target="_blank" rel="noreferrer">https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions3ph.py</a></p><p>These definitions are used when you configure a three-phase inverter in the addon:</p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSOR_DEFINITIONS</span><span style="color:#E1E4E8;">: </span><span style="color:#9ECBFF;">three-phase</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSOR_DEFINITIONS</span><span style="color:#24292E;">: </span><span style="color:#032F62;">three-phase</span></span></code></pre></div><h2 id="three-phase-high-voltage-inverter-sensor-definitions" tabindex="-1">Three Phase High Voltage Inverter Sensor Definitions <a class="header-anchor" href="#three-phase-high-voltage-inverter-sensor-definitions" aria-label="Permalink to &quot;Three Phase High Voltage Inverter Sensor Definitions&quot;">​</a></h2><p>You can find all the definitions here: <a href="https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions3phhv.py" target="_blank" rel="noreferrer">https://github.com/kellerza/sunsynk/blob/main/src/sunsynk/definitions3phhv.py</a></p><p>These definitions are used when you configure a three-phase inverter in the addon:</p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSOR_DEFINITIONS</span><span style="color:#E1E4E8;">: </span><span style="color:#9ECBFF;">three-phase-hv</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSOR_DEFINITIONS</span><span style="color:#24292E;">: </span><span style="color:#032F62;">three-phase-hv</span></span></code></pre></div><h2 id="groups-of-sensors" tabindex="-1">Groups of sensors <a class="header-anchor" href="#groups-of-sensors" aria-label="Permalink to &quot;Groups of sensors&quot;">​</a></h2><p>Sensor groups will allow you to add several sensors with a single entry.</p><h3 id="energy-management" tabindex="-1">Energy management <a class="header-anchor" href="#energy-management" aria-label="Permalink to &quot;Energy management&quot;">​</a></h3><p>These sensors are mostly related to energy or kWh and required for the Home Assistant <a href="./../guide/energy-management">Energy Management</a></p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSORS</span><span style="color:#E1E4E8;">:</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">energy_management</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSORS</span><span style="color:#24292E;">:</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">energy_management</span></span></code></pre></div><details class="details custom-block"><summary>Sensors included</summary><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#9ECBFF;">total_battery_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">total_battery_discharge</span></span>
<span class="line"><span style="color:#9ECBFF;">total_grid_export</span></span>
<span class="line"><span style="color:#9ECBFF;">total_grid_import</span></span>
<span class="line"><span style="color:#9ECBFF;">total_pv_energy</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#032F62;">total_battery_charge</span></span>
<span class="line"><span style="color:#032F62;">total_battery_discharge</span></span>
<span class="line"><span style="color:#032F62;">total_grid_export</span></span>
<span class="line"><span style="color:#032F62;">total_grid_import</span></span>
<span class="line"><span style="color:#032F62;">total_pv_energy</span></span></code></pre></div></details><h3 id="power-flow-card-power-flow-card" tabindex="-1">Power flow card: <code>power_flow_card</code> <a class="header-anchor" href="#power-flow-card-power-flow-card" aria-label="Permalink to &quot;Power flow card: \`power_flow_card\`&quot;">​</a></h3><p>These are all sensors used by the <a href="./../examples/lovelace#sunsynk-power-flow-card">Power Flow Card</a></p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSORS</span><span style="color:#E1E4E8;">:</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">power_flow_card</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSORS</span><span style="color:#24292E;">:</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">power_flow_card</span></span></code></pre></div><details class="details custom-block"><summary>Sensors included</summary><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#9ECBFF;">aux_power</span></span>
<span class="line"><span style="color:#9ECBFF;">battery_current</span></span>
<span class="line"><span style="color:#9ECBFF;">battery_power</span></span>
<span class="line"><span style="color:#9ECBFF;">battery_soc</span></span>
<span class="line"><span style="color:#9ECBFF;">battery_voltage</span></span>
<span class="line"><span style="color:#9ECBFF;">day_battery_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">day_battery_discharge</span></span>
<span class="line"><span style="color:#9ECBFF;">day_grid_export</span></span>
<span class="line"><span style="color:#9ECBFF;">day_grid_import</span></span>
<span class="line"><span style="color:#9ECBFF;">day_load_energy</span></span>
<span class="line"><span style="color:#9ECBFF;">day_pv_energy</span></span>
<span class="line"><span style="color:#9ECBFF;">essential_power</span></span>
<span class="line"><span style="color:#9ECBFF;">grid_connected</span></span>
<span class="line"><span style="color:#9ECBFF;">grid_ct_power</span></span>
<span class="line"><span style="color:#9ECBFF;">grid_frequency</span></span>
<span class="line"><span style="color:#9ECBFF;">grid_power</span></span>
<span class="line"><span style="color:#9ECBFF;">grid_voltage</span></span>
<span class="line"><span style="color:#9ECBFF;">inverter_current</span></span>
<span class="line"><span style="color:#9ECBFF;">inverter_power</span></span>
<span class="line"><span style="color:#9ECBFF;">load_frequency</span></span>
<span class="line"><span style="color:#9ECBFF;">non_essential_power</span></span>
<span class="line"><span style="color:#9ECBFF;">overall_state</span></span>
<span class="line"><span style="color:#9ECBFF;">priority_load</span></span>
<span class="line"><span style="color:#9ECBFF;">pv1_current</span></span>
<span class="line"><span style="color:#9ECBFF;">pv1_power</span></span>
<span class="line"><span style="color:#9ECBFF;">pv1_voltage</span></span>
<span class="line"><span style="color:#9ECBFF;">use_timer</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#032F62;">aux_power</span></span>
<span class="line"><span style="color:#032F62;">battery_current</span></span>
<span class="line"><span style="color:#032F62;">battery_power</span></span>
<span class="line"><span style="color:#032F62;">battery_soc</span></span>
<span class="line"><span style="color:#032F62;">battery_voltage</span></span>
<span class="line"><span style="color:#032F62;">day_battery_charge</span></span>
<span class="line"><span style="color:#032F62;">day_battery_discharge</span></span>
<span class="line"><span style="color:#032F62;">day_grid_export</span></span>
<span class="line"><span style="color:#032F62;">day_grid_import</span></span>
<span class="line"><span style="color:#032F62;">day_load_energy</span></span>
<span class="line"><span style="color:#032F62;">day_pv_energy</span></span>
<span class="line"><span style="color:#032F62;">essential_power</span></span>
<span class="line"><span style="color:#032F62;">grid_connected</span></span>
<span class="line"><span style="color:#032F62;">grid_ct_power</span></span>
<span class="line"><span style="color:#032F62;">grid_frequency</span></span>
<span class="line"><span style="color:#032F62;">grid_power</span></span>
<span class="line"><span style="color:#032F62;">grid_voltage</span></span>
<span class="line"><span style="color:#032F62;">inverter_current</span></span>
<span class="line"><span style="color:#032F62;">inverter_power</span></span>
<span class="line"><span style="color:#032F62;">load_frequency</span></span>
<span class="line"><span style="color:#032F62;">non_essential_power</span></span>
<span class="line"><span style="color:#032F62;">overall_state</span></span>
<span class="line"><span style="color:#032F62;">priority_load</span></span>
<span class="line"><span style="color:#032F62;">pv1_current</span></span>
<span class="line"><span style="color:#032F62;">pv1_power</span></span>
<span class="line"><span style="color:#032F62;">pv1_voltage</span></span>
<span class="line"><span style="color:#032F62;">use_timer</span></span></code></pre></div></details><h3 id="settings" tabindex="-1">Settings <a class="header-anchor" href="#settings" aria-label="Permalink to &quot;Settings&quot;">​</a></h3><p>Sensors used for changing the System Operating Mode - see <a href="./../examples/lovelace-settings">here</a></p><p>These can be under <code>SENSORS</code> or <code>SENSORS_FIRST_INVERTER</code></p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#85E89D;">SENSORS_FIRST_INVERTER</span><span style="color:#E1E4E8;">:</span></span>
<span class="line"><span style="color:#E1E4E8;">  - </span><span style="color:#9ECBFF;">settings</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#22863A;">SENSORS_FIRST_INVERTER</span><span style="color:#24292E;">:</span></span>
<span class="line"><span style="color:#24292E;">  - </span><span style="color:#032F62;">settings</span></span></code></pre></div><details class="details custom-block"><summary>Sensors included</summary><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#9ECBFF;">load_limit</span></span>
<span class="line"><span style="color:#9ECBFF;">prog1_capacity</span></span>
<span class="line"><span style="color:#9ECBFF;">prog1_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">prog1_power</span></span>
<span class="line"><span style="color:#9ECBFF;">prog1_time</span></span>
<span class="line"><span style="color:#9ECBFF;">prog2_capacity</span></span>
<span class="line"><span style="color:#9ECBFF;">prog2_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">prog2_power</span></span>
<span class="line"><span style="color:#9ECBFF;">prog2_time</span></span>
<span class="line"><span style="color:#9ECBFF;">prog3_capacity</span></span>
<span class="line"><span style="color:#9ECBFF;">prog3_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">prog3_power</span></span>
<span class="line"><span style="color:#9ECBFF;">prog3_time</span></span>
<span class="line"><span style="color:#9ECBFF;">prog4_capacity</span></span>
<span class="line"><span style="color:#9ECBFF;">prog4_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">prog4_power</span></span>
<span class="line"><span style="color:#9ECBFF;">prog4_time</span></span>
<span class="line"><span style="color:#9ECBFF;">prog5_capacity</span></span>
<span class="line"><span style="color:#9ECBFF;">prog5_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">prog5_power</span></span>
<span class="line"><span style="color:#9ECBFF;">prog5_time</span></span>
<span class="line"><span style="color:#9ECBFF;">prog6_capacity</span></span>
<span class="line"><span style="color:#9ECBFF;">prog6_charge</span></span>
<span class="line"><span style="color:#9ECBFF;">prog6_power</span></span>
<span class="line"><span style="color:#9ECBFF;">prog6_time</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#032F62;">load_limit</span></span>
<span class="line"><span style="color:#032F62;">prog1_capacity</span></span>
<span class="line"><span style="color:#032F62;">prog1_charge</span></span>
<span class="line"><span style="color:#032F62;">prog1_power</span></span>
<span class="line"><span style="color:#032F62;">prog1_time</span></span>
<span class="line"><span style="color:#032F62;">prog2_capacity</span></span>
<span class="line"><span style="color:#032F62;">prog2_charge</span></span>
<span class="line"><span style="color:#032F62;">prog2_power</span></span>
<span class="line"><span style="color:#032F62;">prog2_time</span></span>
<span class="line"><span style="color:#032F62;">prog3_capacity</span></span>
<span class="line"><span style="color:#032F62;">prog3_charge</span></span>
<span class="line"><span style="color:#032F62;">prog3_power</span></span>
<span class="line"><span style="color:#032F62;">prog3_time</span></span>
<span class="line"><span style="color:#032F62;">prog4_capacity</span></span>
<span class="line"><span style="color:#032F62;">prog4_charge</span></span>
<span class="line"><span style="color:#032F62;">prog4_power</span></span>
<span class="line"><span style="color:#032F62;">prog4_time</span></span>
<span class="line"><span style="color:#032F62;">prog5_capacity</span></span>
<span class="line"><span style="color:#032F62;">prog5_charge</span></span>
<span class="line"><span style="color:#032F62;">prog5_power</span></span>
<span class="line"><span style="color:#032F62;">prog5_time</span></span>
<span class="line"><span style="color:#032F62;">prog6_capacity</span></span>
<span class="line"><span style="color:#032F62;">prog6_charge</span></span>
<span class="line"><span style="color:#032F62;">prog6_power</span></span>
<span class="line"><span style="color:#032F62;">prog6_time</span></span></code></pre></div></details>`,38),o=[l];function t(r,c,i,y,d,h){return a(),n("div",null,o)}const E=s(p,[["render",t]]);export{F as __pageData,E as default};
