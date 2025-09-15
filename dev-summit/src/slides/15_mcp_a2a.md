
# Steuerung im Nebel: Wie KI-Agenten navigieren

<h2 style="text-align: center; margin-bottom: 2rem;">MCP vs. A2A</h2>

<div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 2rem; align-items: center;">
	<ul style="list-style-type: disc; font-size: clamp(0.9rem, 2vw, 1.2rem); text-align: left;">
		<li><b>Digitale Seekarten & GPS-Historie</b>: kennt die Historie, frühere Gefahren und hat das Ziel im Auge</li>
		<li><b>Schiffs-Telemetrie</b>: liefert Echtzeitdaten über das Schiff und die Ladung</li>
	</ul>
	<img src="images/mcp-a2a.png" alt="MCP vs. A2A" style="max-width: 100%; height: 320px; object-fit: contain;" />
	<ul style="list-style-type: disc; font-size: clamp(0.9rem, 2vw, 1.2rem); text-align: left;">
		<li><b>Navigations-Agent</b>: kommuniziert mit dem Maschinenraum-Agenten für die beste Route</li>
		<li><b>Kommunikations-Agent</b>: hört den Funk ab und warnt das Team</li>
	</ul>
</div>