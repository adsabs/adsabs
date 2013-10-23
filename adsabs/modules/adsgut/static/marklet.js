(function(){

	// the minimum version of jQuery we want
	var v = "1.3.2";
	// check prior inclusion and version
	if (window.jQuery === undefined || window.jQuery.fn.jquery < v) {
		var done = false;
		var script = document.createElement("script");
		script.src = "http://ajax.googleapis.com/ajax/libs/jquery/" + v + "/jquery.min.js";
		script.onload = script.onreadystatechange = function(){
			if (!done && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
				done = true;
				initMyBookmarklet();
			}
		};
		document.getElementsByTagName("head")[0].appendChild(script);
	} else {
		initMyBookmarklet();
	}
	
	function initMyBookmarklet() {
		(window.myBookmarklet = function() {
			// your JavaScript code goes here!
			var items=[];
			$(".searchresult > .span1 > .checkbox > input:checked").each(
					function(){items.push("ads/"+$(this).attr("value"));}); 
			var itemstring=items.join(":");
			var loc = document.location;
			var locinfo = loc.pathname+loc.search
			if (items.length > 0){
				open("http://localhost:4000/postform/ads/pub/html?items="+itemstring, width="750", height="300");
			} else {
				open("http://localhost:4000/postform/ads/search/html?items="+encodeURIComponent(locinfo), width="750", height="300");
			}
		})();
	}

})();

