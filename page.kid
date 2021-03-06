<html>
<head>
 <title>Today's train times at Jack London Square</title>
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
div.notice {
 margin: 1em;
 padding: .5em;
 font-size: 70%;
 border: 1px solid #ddd;

}
div.capitol {
 margin: 1em;
 padding: .5em;
 font-size: 80%;
 border: 2px solid #ddd;
}
 
}
</style>
<body>
<h1>Today's train times at Jack London Square</h1>
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

<div class="capitol">
If you are a Geocacher, or are interested in Geocaching, there is a cache at the Jack London Square Amtrak Station. Please see <a
href="http://www.geocaching.com/seek/cache_details.aspx?wp=GC14gff">the cache page</a> for more details. There is also a waymark of the
JLS station. Please see the <a 
href="http://www.waymarking.com/wm/details.aspx?f=1&amp;guid=642a356b-9565-4d32-b160-6a745c087476">C.L. Dellums Station</a> 
waymark page for more information.
 </div>

<div class="capitol">
The Capitol Corridor recently put up a service to view train times for any station. <b> Unfortunately, their page is down at the 
moment,</b> but when it's up, you can view their station selection page by clicking 
<a href="http://www.capitolcorridor.org/schedules/train_status/"> here.</a> We're not responsible for the information on this page, especially because it's compiled by a different method than we use.
</div>

<div class="notice">
This is an automated site using information from Amtrak at <a href="http://tickets.amtrak.com/itd/amtrak">this search page</a>. We can't be
held responsible for the information they provide us. This page 
may not work all the time and may disappear completely
without notice. Please send comments to traintimes@bigasterisk.com
</div>

</body>
</html>
