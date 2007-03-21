<html>
<head>
 <title>Today's train times</title>
</head>
<style type="text/css">
table.sample {
	border-width: 1px 1px 1px 1px;
	border-spacing: 2px;
	border-style: outset outset outset outset;
	border-color: gray gray gray gray;
	border-collapse: collapse;
	background-color: white;
}
table.sample th {
	border-width: 1px 1px 1px 1px;
	padding: 3px 3px 3px 3px;
	border-style: inset inset inset inset;
	border-color: gray gray gray gray;
	background-color: #cccccc;
	-moz-border-radius: 0px 0px 0px 0px;
}
table.sample td {
	border-width: 1px 1px 1px 1px;
	padding: 3px 3px 3px 3px;
	border-style: inset inset inset inset;
	border-color: gray gray gray gray;
	-moz-border-radius: 0px 0px 0px 0px;
        font-family: sans-serif;
}
</style>
<body>
<p><i>Last scan at ${now}</i></p>

<p>Data from <a href="http://tickets.amtrak.com/itd/amtrak">Amtrak</a></p>

<p>Times are on ${today}</p>

<table class="sample" border="1">
<tr>
 <th>Train number</th>
 <th>Scheduled</th>
 <th>Actual / Estimated</th>
 <th>Note</th> 
</tr>
${XML(rowSection)}
</table>
</body>
</html>
