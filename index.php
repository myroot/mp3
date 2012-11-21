<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="viewport" content="user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, width=device-width" />
<title>Youtube download & upload google music</title>
<script src="js/jquery-1.6.1.min.js"></script>
<link rel="stylesheet" type="text/css" href="daum.css" />

<style>
#searchbar {
padding:10px 20px 20px;
}
#log {
  padding:10px 20px 20px;
}
body{
	padding:10px 10px;
}
</style>

</head>
<body>
<script>

var last_id = '';
var timer_id = {};

function jsonp_test(){
	$.ajax({
		url : "http://toors.cafe24.com:2323/test",
		dataType : "jsonp",
		jsonp : "callback",
		success : function(d){
			$('#test').html(d.time);
		}
	});
}

function polling_status_start(key){
	timer = setInterval(function(){polling_status(key)},2000);
	timer_id[key] = timer;
}

function polling_status(key){
	$.ajax({
		url : "http://toors.cafe24.com:2323/update?key="+key,
		dataType : "jsonp",
		jsonp : "callback",
		success : function(d){
			result = d.status;
			if( result == 'fail' || result == 'complete' ){
				$('#'+d.key).html(result);
				clearInterval(timer_id[d.key]);
				if( result == 'complete' ){
					$('#'+d.key).html('<a href='+d.path+' target=_blank>'+d.path+'</a>');
				}
					
			}else{
				$('#'+d.key).html(result+"...");
				$('#'+d.key+'_progress').html(d.progress);
				
			}
		}
	});
	
}

function request_download(key,upload){
	//alert(key);
	//alert(upload);
	$.ajax({
		url : "http://toors.cafe24.com:2323/down?key="+key+'&upload='+upload,
		dataType : "jsonp",
		jsonp : "callback",
		success : function(d){
			result = d.status;
			if( result == 'ok' ){
				$('#'+d.key).html('waitng...');
				polling_status_start(d.key);
			}else{
				$('#'+d.key).html('Fail');
			}
		}
	});
}

function search(){
	var upload = '0';
	var checked = '';
	if( $('#gmusic').attr('checked') ){
		upload = '1';
		checked = 'checked'
	}
	if( $('#url').attr('value') == '')
		return false;
	if( $('#url').attr('value').indexOf('http://www.youtube.com/watch') != -1 ){
		var url =  $('#url').attr('value');
		idx = url.indexOf('v=');
		idx2 = url.indexOf('&', idx);

		if( idx2 != -1 )
			id = url.substring(idx+2,idx2);
		else
			id = url.substring(idx+2);	
		//alert('http://www.youtube.com/embed/'+id);
		$('#logwin').prepend('<li><iframe width=640 height=360 src="http://www.youtube.com/embed/'+id+'"></iframe></li>');
		$('#logwin').prepend('<li>http://www.youtube.com/embed/'+id+' <input type=checkbox id='+id+'_upload '+ checked +'> Google music upload</li>');
		$('#logwin').prepend('<li><div id='+id+'_progress></div>');
		$('#logwin').prepend('<li><div id='+id+'></div>');
		last_id = id;
		request_download(id,upload);
	}
	$('#url').attr('value', '');
	return false;
}

function remove_default(){
	if($('#url').attr('value') == 'http://www.youtube.com/watch?v='){
		$('#url').attr('value', '');		
	}
}
function set_default(){
	if($('#url').attr('value') == ''){
		$('#url').attr('value', 'http://www.youtube.com/watch?v=');		
	}
}

</script>
<h3>YouTube music download & upload google music </h3>
<form action="/" method=post onsubmit="return search();">
<div id=searchbar>
URL: <input type=text id=url name=url style=width:100% value='http://www.youtube.com/watch?v=' onFocus=remove_default() onBlur=set_default()>
<input type="checkbox" id='gmusic' name="gmusic" value="1" checked> Upload google music
</div>
</form>
<div id=log>
<ul id=logwin>
</ul>
</div>
</body>
</html>
