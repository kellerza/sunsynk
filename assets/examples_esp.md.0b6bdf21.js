import{_ as s,o as n,c as a,Q as e}from"./chunks/framework.dfcac6be.js";const h=JSON.parse('{"title":"ESP integration","description":"","frontmatter":{},"headers":[],"relativePath":"examples/esp.md","filePath":"examples/esp.md","lastUpdated":1707245027000}'),t={name:"examples/esp.md"},l=e(`<h1 id="esp-integration" tabindex="-1">ESP integration <a class="header-anchor" href="#esp-integration" aria-label="Permalink to &quot;ESP integration&quot;">​</a></h1><p>The ESP integration uses a combination of mysensors + Frontend</p><p>Init your ESP sensor with the following <strong>mysensors.py</strong> entry</p><div class="language-python vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">python</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#F97583;">try</span><span style="color:#E1E4E8;">:</span></span>
<span class="line"><span style="color:#E1E4E8;">    </span><span style="color:#F97583;">from</span><span style="color:#E1E4E8;"> ha_addon_sunsynk_multi.esp </span><span style="color:#F97583;">import</span><span style="color:#E1E4E8;"> </span><span style="color:#79B8FF;">ESP</span></span>
<span class="line"><span style="color:#E1E4E8;">    ESP(</span></span>
<span class="line"><span style="color:#E1E4E8;">        </span><span style="color:#FFAB70;">api_key</span><span style="color:#F97583;">=</span><span style="color:#9ECBFF;">&quot;xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx&quot;</span><span style="color:#E1E4E8;">,</span></span>
<span class="line"><span style="color:#E1E4E8;">        </span><span style="color:#FFAB70;">area_id</span><span style="color:#F97583;">=</span><span style="color:#9ECBFF;">&quot;jhbcitypower2-2-victorypark&quot;</span><span style="color:#E1E4E8;">,</span></span>
<span class="line"><span style="color:#E1E4E8;">        </span><span style="color:#FFAB70;">ha_prefix</span><span style="color:#F97583;">=</span><span style="color:#9ECBFF;">&quot;eskom_vp&quot;</span><span style="color:#E1E4E8;">,</span></span>
<span class="line"><span style="color:#E1E4E8;">    )</span></span>
<span class="line"><span style="color:#F97583;">except</span><span style="color:#E1E4E8;"> </span><span style="color:#79B8FF;">ImportError</span><span style="color:#E1E4E8;">:</span></span>
<span class="line"><span style="color:#E1E4E8;">    </span><span style="color:#F97583;">pass</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#D73A49;">try</span><span style="color:#24292E;">:</span></span>
<span class="line"><span style="color:#24292E;">    </span><span style="color:#D73A49;">from</span><span style="color:#24292E;"> ha_addon_sunsynk_multi.esp </span><span style="color:#D73A49;">import</span><span style="color:#24292E;"> </span><span style="color:#005CC5;">ESP</span></span>
<span class="line"><span style="color:#24292E;">    ESP(</span></span>
<span class="line"><span style="color:#24292E;">        </span><span style="color:#E36209;">api_key</span><span style="color:#D73A49;">=</span><span style="color:#032F62;">&quot;xxxxxxxx-xxxxxxxx-xxxxxxxx-xxxxxxxx&quot;</span><span style="color:#24292E;">,</span></span>
<span class="line"><span style="color:#24292E;">        </span><span style="color:#E36209;">area_id</span><span style="color:#D73A49;">=</span><span style="color:#032F62;">&quot;jhbcitypower2-2-victorypark&quot;</span><span style="color:#24292E;">,</span></span>
<span class="line"><span style="color:#24292E;">        </span><span style="color:#E36209;">ha_prefix</span><span style="color:#D73A49;">=</span><span style="color:#032F62;">&quot;eskom_vp&quot;</span><span style="color:#24292E;">,</span></span>
<span class="line"><span style="color:#24292E;">    )</span></span>
<span class="line"><span style="color:#D73A49;">except</span><span style="color:#24292E;"> </span><span style="color:#005CC5;">ImportError</span><span style="color:#24292E;">:</span></span>
<span class="line"><span style="color:#24292E;">    </span><span style="color:#D73A49;">pass</span></span></code></pre></div><p>The following should be saved in you HA config folder <code>/config/custom_templates/loadshed.jinja</code></p><div class="language-jinja vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">jinja</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#e1e4e8;">{% macro loadshed_md(espnext) %}</span></span>
<span class="line"><span style="color:#e1e4e8;"></span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set active = (as_timestamp(states(espnext))&lt;=as_timestamp(now())) | bool %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set stage = state_attr(espnext, &quot;note&quot;) %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set t0 = state_attr(espnext, &quot;start&quot;) | as_timestamp | int %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set t1 = state_attr(espnext, &quot;end&quot;) | as_timestamp | int %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set t0_min = (t0|int - as_timestamp(now()))|int // 60 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set t1_min = (t1|int - as_timestamp(now()))|int // 60 %}</span></span>
<span class="line"><span style="color:#e1e4e8;"></span></span>
<span class="line"><span style="color:#e1e4e8;">{%- if stage %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- if not bool(active) %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set mins = t0_min % 60 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set hrs = t0_min // 60 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set alert = &quot;Load Shedding starts in {h}:{m:02d} ({next})&quot;.format(m=mins, h=hrs, next=t0 |</span></span>
<span class="line"><span style="color:#e1e4e8;">timestamp_custom(&quot;%H:%M&quot;, True)) %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- if hrs&gt;12 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">&lt;ha-alert alert-type=&quot;success&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- elif hrs &gt; 1 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">&lt;ha-alert alert-type=&quot;warning&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- else %}</span></span>
<span class="line"><span style="color:#e1e4e8;">&lt;ha-alert alert-type=&quot;error&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- endif %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- else %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set mins = t1_min % 60 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set hrs = t1_min // 60 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set alert = &quot;Load Shedding ends in {h}:{m:02d} ({next})&quot;.format(m=mins, h=hrs, next=t1 |</span></span>
<span class="line"><span style="color:#e1e4e8;">timestamp_custom(&quot;%H:%M&quot;, True)) %}</span></span>
<span class="line"><span style="color:#e1e4e8;">&lt;ha-alert alert-type=&quot;error&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- endif %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- else %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set mins = t0_min % 60 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set hrs = t0_min // 60 % 24 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set days = t0_min // 1440 %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- if (t0 == 0 or t1 == 0) %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set alert = &quot;No Load Shedding&quot; %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- else %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- set alert = &quot;Stage {stage} starts in {d}d {h:02d}:{m:02d} ({next})&quot;.format(stage=stage, d=days, m=mins, h=hrs,</span></span>
<span class="line"><span style="color:#e1e4e8;">next=as_timestamp(start_time) | timestamp_custom(&quot;%H:%M&quot;, True)) %}</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- endif %}</span></span>
<span class="line"><span style="color:#e1e4e8;">&lt;ha-alert alert-type=&quot;success&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#e1e4e8;">{%- endif %}</span></span>
<span class="line"><span style="color:#e1e4e8;"></span></span>
<span class="line"><span style="color:#e1e4e8;">{% endmacro %}</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#24292e;">{% macro loadshed_md(espnext) %}</span></span>
<span class="line"><span style="color:#24292e;"></span></span>
<span class="line"><span style="color:#24292e;">{%- set active = (as_timestamp(states(espnext))&lt;=as_timestamp(now())) | bool %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set stage = state_attr(espnext, &quot;note&quot;) %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set t0 = state_attr(espnext, &quot;start&quot;) | as_timestamp | int %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set t1 = state_attr(espnext, &quot;end&quot;) | as_timestamp | int %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set t0_min = (t0|int - as_timestamp(now()))|int // 60 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set t1_min = (t1|int - as_timestamp(now()))|int // 60 %}</span></span>
<span class="line"><span style="color:#24292e;"></span></span>
<span class="line"><span style="color:#24292e;">{%- if stage %}</span></span>
<span class="line"><span style="color:#24292e;">{%- if not bool(active) %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set mins = t0_min % 60 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set hrs = t0_min // 60 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set alert = &quot;Load Shedding starts in {h}:{m:02d} ({next})&quot;.format(m=mins, h=hrs, next=t0 |</span></span>
<span class="line"><span style="color:#24292e;">timestamp_custom(&quot;%H:%M&quot;, True)) %}</span></span>
<span class="line"><span style="color:#24292e;">{%- if hrs&gt;12 %}</span></span>
<span class="line"><span style="color:#24292e;">&lt;ha-alert alert-type=&quot;success&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#24292e;">{%- elif hrs &gt; 1 %}</span></span>
<span class="line"><span style="color:#24292e;">&lt;ha-alert alert-type=&quot;warning&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#24292e;">{%- else %}</span></span>
<span class="line"><span style="color:#24292e;">&lt;ha-alert alert-type=&quot;error&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#24292e;">{%- endif %}</span></span>
<span class="line"><span style="color:#24292e;">{%- else %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set mins = t1_min % 60 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set hrs = t1_min // 60 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set alert = &quot;Load Shedding ends in {h}:{m:02d} ({next})&quot;.format(m=mins, h=hrs, next=t1 |</span></span>
<span class="line"><span style="color:#24292e;">timestamp_custom(&quot;%H:%M&quot;, True)) %}</span></span>
<span class="line"><span style="color:#24292e;">&lt;ha-alert alert-type=&quot;error&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#24292e;">{%- endif %}</span></span>
<span class="line"><span style="color:#24292e;">{%- else %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set mins = t0_min % 60 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set hrs = t0_min // 60 % 24 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set days = t0_min // 1440 %}</span></span>
<span class="line"><span style="color:#24292e;">{%- if (t0 == 0 or t1 == 0) %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set alert = &quot;No Load Shedding&quot; %}</span></span>
<span class="line"><span style="color:#24292e;">{%- else %}</span></span>
<span class="line"><span style="color:#24292e;">{%- set alert = &quot;Stage {stage} starts in {d}d {h:02d}:{m:02d} ({next})&quot;.format(stage=stage, d=days, m=mins, h=hrs,</span></span>
<span class="line"><span style="color:#24292e;">next=as_timestamp(start_time) | timestamp_custom(&quot;%H:%M&quot;, True)) %}</span></span>
<span class="line"><span style="color:#24292e;">{%- endif %}</span></span>
<span class="line"><span style="color:#24292e;">&lt;ha-alert alert-type=&quot;success&quot;&gt;{{ alert }}&lt;/ha-alert&gt;</span></span>
<span class="line"><span style="color:#24292e;">{%- endif %}</span></span>
<span class="line"><span style="color:#24292e;"></span></span>
<span class="line"><span style="color:#24292e;">{% endmacro %}</span></span></code></pre></div><p>You can now add this card to your frontend to create a status of loadshedding</p><div class="language-yaml vp-adaptive-theme"><button title="Copy Code" class="copy"></button><span class="lang">yaml</span><pre class="shiki github-dark vp-code-dark"><code><span class="line"><span style="color:#E1E4E8;">- </span><span style="color:#85E89D;">type</span><span style="color:#E1E4E8;">: </span><span style="color:#9ECBFF;">markdown</span></span>
<span class="line"><span style="color:#E1E4E8;">    </span><span style="color:#85E89D;">content</span><span style="color:#E1E4E8;">: </span><span style="color:#9ECBFF;">&#39;{% from &quot;loadshed.jinja&quot; import loadshed_md %} {{ loadshed_md(&quot;sensor.eskom_vp_next&quot;) }}&#39;</span></span></code></pre><pre class="shiki github-light vp-code-light"><code><span class="line"><span style="color:#24292E;">- </span><span style="color:#22863A;">type</span><span style="color:#24292E;">: </span><span style="color:#032F62;">markdown</span></span>
<span class="line"><span style="color:#24292E;">    </span><span style="color:#22863A;">content</span><span style="color:#24292E;">: </span><span style="color:#032F62;">&#39;{% from &quot;loadshed.jinja&quot; import loadshed_md %} {{ loadshed_md(&quot;sensor.eskom_vp_next&quot;) }}&#39;</span></span></code></pre></div>`,8),p=[l];function o(c,r,i,y,d,m){return n(),a("div",null,p)}const x=s(t,[["render",o]]);export{h as __pageData,x as default};
