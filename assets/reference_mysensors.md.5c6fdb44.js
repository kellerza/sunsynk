import{_ as s,c as n,o as a,Q as l}from"./chunks/framework.7f5240a6.js";const u=JSON.parse('{"title":"Custom Sensors","description":"","frontmatter":{},"headers":[],"relativePath":"reference/mysensors.md","lastUpdated":1692274446000}'),p={name:"reference/mysensors.md"},e=l(`<h1 id="custom-sensors" tabindex="-1">Custom Sensors <a class="header-anchor" href="#custom-sensors" aria-label="Permalink to &quot;Custom Sensors&quot;">​</a></h1><p>You can add custom sensors by creating a sensors definition file called in <code>/share/hass-addon-sunsynk/mysensors.py</code>.</p><p>In it&#39;s most basic form a sensor the RS486 register and a name. You can find the RS485 protocol document at various places online, search the <a href="https://www.powerforum.co.za" target="_blank" rel="noreferrer">Power Forum</a> or <a href="https://github.com/kellerza/sunsynk/issues/59" target="_blank" rel="noreferrer">Github issue #59</a></p><p>The <code>/share/</code> folder can be accessed through the Samba addon in Home Assistant. You can create the <code>hass-addon-sunsynk</code> folder &amp; the <code>mysensors.py</code> file</p><p>This is a Python file and follows the same logic as the definitions.py &amp; definitions3p.py. It exposes a single <code>SENSORS</code> global variable to which you can add the individual sensor definitions.</p><p>An example <code>mysensors.py</code> file:</p><div class="language-python"><button title="Copy Code" class="copy"></button><span class="lang">python</span><pre class="shiki material-theme-palenight"><code><span class="line"><span style="color:#89DDFF;font-style:italic;">from</span><span style="color:#A6ACCD;"> sunsynk </span><span style="color:#89DDFF;font-style:italic;">import</span><span style="color:#A6ACCD;"> AMPS</span><span style="color:#89DDFF;">,</span><span style="color:#A6ACCD;"> CELSIUS</span><span style="color:#89DDFF;">,</span><span style="color:#A6ACCD;"> KWH</span><span style="color:#89DDFF;">,</span><span style="color:#A6ACCD;"> VOLT</span><span style="color:#89DDFF;">,</span><span style="color:#A6ACCD;"> WATT</span></span>
<span class="line"><span style="color:#89DDFF;font-style:italic;">from</span><span style="color:#A6ACCD;"> sunsynk</span><span style="color:#89DDFF;">.</span><span style="color:#A6ACCD;">rwsensors </span><span style="color:#89DDFF;font-style:italic;">import</span><span style="color:#A6ACCD;"> NumberRWSensor</span><span style="color:#89DDFF;">,</span><span style="color:#A6ACCD;"> SelectRWSensor</span><span style="color:#89DDFF;">,</span><span style="color:#A6ACCD;"> TimeRWSensor</span></span>
<span class="line"><span style="color:#89DDFF;font-style:italic;">from</span><span style="color:#A6ACCD;"> sunsynk</span><span style="color:#89DDFF;">.</span><span style="color:#A6ACCD;">sensors </span><span style="color:#89DDFF;font-style:italic;">import</span><span style="color:#A6ACCD;"> </span><span style="color:#89DDFF;">(</span></span>
<span class="line"><span style="color:#A6ACCD;">    MathSensor</span><span style="color:#89DDFF;">,</span></span>
<span class="line"><span style="color:#A6ACCD;">    Sensor</span><span style="color:#89DDFF;">,</span></span>
<span class="line"><span style="color:#A6ACCD;">    SensorDefinitions</span><span style="color:#89DDFF;">,</span></span>
<span class="line"><span style="color:#A6ACCD;">    TempSensor</span><span style="color:#89DDFF;">,</span></span>
<span class="line"><span style="color:#89DDFF;">)</span></span>
<span class="line"></span>
<span class="line"><span style="color:#A6ACCD;">SENSORS </span><span style="color:#89DDFF;">=</span><span style="color:#A6ACCD;"> </span><span style="color:#82AAFF;">SensorDefinitions</span><span style="color:#89DDFF;">()</span></span>
<span class="line"></span>
<span class="line"><span style="color:#A6ACCD;">SENSORS </span><span style="color:#89DDFF;">+=</span><span style="color:#A6ACCD;"> </span><span style="color:#82AAFF;">Sensor</span><span style="color:#89DDFF;">(</span><span style="color:#F78C6C;">178</span><span style="color:#89DDFF;">,</span><span style="color:#82AAFF;"> </span><span style="color:#89DDFF;">&quot;</span><span style="color:#C3E88D;">My Custom Sensor</span><span style="color:#89DDFF;">&quot;</span><span style="color:#89DDFF;">,</span><span style="color:#82AAFF;"> WATT</span><span style="color:#89DDFF;">,</span><span style="color:#82AAFF;"> </span><span style="color:#89DDFF;">-</span><span style="color:#F78C6C;">1</span><span style="color:#89DDFF;">)</span></span>
<span class="line"></span></code></pre></div><p>Once you have a file, you will see it in your addon&#39;s startup log:</p><div class="language-txt"><button title="Copy Code" class="copy"></button><span class="lang">txt</span><pre class="shiki material-theme-palenight"><code><span class="line"><span style="color:#A6ACCD;">2023-03-19 16:25:00,156 INFO    Importing /share/hass-addon-sunsynk/mysensors.py...</span></span>
<span class="line"><span style="color:#A6ACCD;">2023-03-19 16:25:00,158 INFO      custom sensors: my_custom_sensor</span></span>
<span class="line"><span style="color:#A6ACCD;">\`\`\`</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">## Using the sensor</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">Once the sensor is available, you can add it to your configuration:</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">\`\`\`yaml</span></span>
<span class="line"><span style="color:#A6ACCD;">SENSORS:</span></span>
<span class="line"><span style="color:#A6ACCD;"> - my_custom_sensor</span></span>
<span class="line"><span style="color:#A6ACCD;">\`\`\`</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">## More examples</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">### Time sensor</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">::: info</span></span>
<span class="line"><span style="color:#A6ACCD;">Write is only partially implemented in the example below</span></span>
<span class="line"><span style="color:#A6ACCD;">:::</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">::: details</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">\`\`\`python</span></span>
<span class="line"><span style="color:#A6ACCD;">import attr</span></span>
<span class="line"><span style="color:#A6ACCD;">import re</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;"># from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT</span></span>
<span class="line"><span style="color:#A6ACCD;">from sunsynk.rwsensors import RWSensor, ResolveType</span></span>
<span class="line"><span style="color:#A6ACCD;">from sunsynk.sensors import RegType, ValType, SensorDefinitions</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">SENSORS = SensorDefinitions()</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">@attr.define(slots=True, eq=False)</span></span>
<span class="line"><span style="color:#A6ACCD;">class SystemTimeRWSensor(RWSensor):</span></span>
<span class="line"><span style="color:#A6ACCD;">    &quot;&quot;&quot;Read &amp; write time sensor.&quot;&quot;&quot;</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">    def value_to_reg(self, value: ValType, resolve: ResolveType) -&gt; RegType:</span></span>
<span class="line"><span style="color:#A6ACCD;">        &quot;&quot;&quot;Get the reg value from a display value.&quot;&quot;&quot;</span></span>
<span class="line"><span style="color:#A6ACCD;">        redt = re.compile(r&quot;(2\\d{3})-(\\d{2})-(\\d{2}) (\\d{2}):(\\d{2}):(\\d{2})&quot;)</span></span>
<span class="line"><span style="color:#A6ACCD;">        match = redt.fullmatch(value)</span></span>
<span class="line"><span style="color:#A6ACCD;">        if not match:</span></span>
<span class="line"><span style="color:#A6ACCD;">            raise ValueError(&quot;Invalid datetime {value}&quot;)</span></span>
<span class="line"><span style="color:#A6ACCD;">        y, m, d = int(match.group(1)) - 2000, int(match.group(2)), int(match.group(3))</span></span>
<span class="line"><span style="color:#A6ACCD;">        h, mn, s = int(match.group(4)), int(match.group(5)), int(match.group(6))</span></span>
<span class="line"><span style="color:#A6ACCD;">        regs = (</span></span>
<span class="line"><span style="color:#A6ACCD;">            (y &lt;&lt; 8) + m,</span></span>
<span class="line"><span style="color:#A6ACCD;">            (d &lt;&lt; 8) + h,</span></span>
<span class="line"><span style="color:#A6ACCD;">            (mn &lt;&lt; 8) + s,</span></span>
<span class="line"><span style="color:#A6ACCD;">        )</span></span>
<span class="line"><span style="color:#A6ACCD;">        raise ValueError(f&quot;{y}-{m:02}-{d:02} {h}:{mn:02}:{s:02} ==&gt; {regs}&quot;)</span></span>
<span class="line"><span style="color:#A6ACCD;">        return regs</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">    def reg_to_value(self, regs: RegType) -&gt; ValType:</span></span>
<span class="line"><span style="color:#A6ACCD;">        &quot;&quot;&quot;Decode the register.&quot;&quot;&quot;</span></span>
<span class="line"><span style="color:#A6ACCD;">        y = ((regs[0] &amp; 0xFF00) &gt;&gt; 8) + 2000</span></span>
<span class="line"><span style="color:#A6ACCD;">        m = regs[0] &amp; 0xFF</span></span>
<span class="line"><span style="color:#A6ACCD;">        d = (regs[1] &amp; 0xFF00) &gt;&gt; 8</span></span>
<span class="line"><span style="color:#A6ACCD;">        h = regs[1] &amp; 0xFF</span></span>
<span class="line"><span style="color:#A6ACCD;">        mn = (regs[2] &amp; 0xFF00) &gt;&gt; 8</span></span>
<span class="line"><span style="color:#A6ACCD;">        s = regs[2] &amp; 0xFF</span></span>
<span class="line"><span style="color:#A6ACCD;">        return f&quot;{y}-{m:02}-{d:02} {h}:{mn:02}:{s:02}&quot;</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">SENSORS += SystemTimeRWSensor((22, 23, 24), &quot;Date&quot;, unit=&quot;&quot;)</span></span>
<span class="line"><span style="color:#A6ACCD;">\`\`\`</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span>
<span class="line"><span style="color:#A6ACCD;">:::</span></span>
<span class="line"><span style="color:#A6ACCD;"></span></span></code></pre></div>`,9),o=[e];function t(r,c,i,A,C,y){return a(),n("div",null,o)}const m=s(p,[["render",t]]);export{u as __pageData,m as default};
