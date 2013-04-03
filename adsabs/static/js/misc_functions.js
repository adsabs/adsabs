/**
 * 
 */

//definition of a new jQuery method to set the cursor at a certain point of the textfield
/**** thanks to Mark from StackOverflow ****/
$.fn.selectRange = function(start, end) {
    return this.each(function() {
        if (this.setSelectionRange) {
            this.focus();
            this.setSelectionRange(start, end);
        } else if (this.createTextRange) {
            var range = this.createTextRange();
            range.collapse(true);
            range.moveEnd('character', end);
            range.moveStart('character', start);
            range.select();
        }
    });
};

//definition of an escaping method
RegExp.escape = function(text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
}

//###########################################################################################//
// definition of the spinner extension for jquery
$.fn.spin = function(opts, color) {
	var presets = {
		"tiny": { lines: 8, length: 2, width: 2, radius: 3 },
		"small": { lines: 8, length: 4, width: 3, radius: 5 },
		"large": { lines: 10, length: 8, width: 4, radius: 8 },
		"ads_facets" : {
				  lines: 11, // The number of lines to draw
				  length: 5, // The length of each line
				  width: 2, // The line thickness
				  radius: 2, // The radius of the inner circle
				  corners: 1, // Corner roundness (0..1)
				  rotate: 0, // The rotation offset
				  color: '#000', // #rgb or #rrggbb
				  speed: 1.2, // Rounds per second
				  trail: 60, // Afterglow percentage
				  shadow: false, // Whether to render a shadow
				  hwaccel: false, // Whether to use hardware acceleration
				  className: 'spinner', // The CSS class to assign to the spinner
				  zIndex: 2e9, // The z-index (defaults to 2000000000)
				  top: 'auto', // Top position relative to parent in px
				  left: 'auto' // Left position relative to parent in px
				}
	};
	if (Spinner) {
		return this.each(function() {
			var $this = $(this),
				data = $this.data();
			
			if (data.spinner) {
				data.spinner.stop();
				delete data.spinner;
			}
			if (opts !== false) {
				if (typeof opts === "string") {
					if (opts in presets) {
						opts = presets[opts];
					} else {
						opts = {};
					}
					if (color) {
						opts.color = color;
					}
				}
				data.spinner = new Spinner($.extend({color: $this.css('color')}, opts)).spin(this);
			}
		});
	} else {
		throw "Spinner class not available.";
	}
};

//###########################################################################################//
//simple global functions
function isInt(n) {
   return n % 1 == 0;
}

//###########################################################################################//
// Adds compatibility to the old browsers to the keys method of an object

if (!Object.keys) {
	  Object.keys = (function () {
	    var hasOwnProperty = Object.prototype.hasOwnProperty,
	        hasDontEnumBug = !({toString: null}).propertyIsEnumerable('toString'),
	        dontEnums = [
	          'toString',
	          'toLocaleString',
	          'valueOf',
	          'hasOwnProperty',
	          'isPrototypeOf',
	          'propertyIsEnumerable',
	          'constructor'
	        ],
	        dontEnumsLength = dontEnums.length;
	 
	    return function (obj) {
	      if (typeof obj !== 'object' && typeof obj !== 'function' || obj === null) throw new TypeError('Object.keys called on non-object');
	 
	      var result = [];
	 
	      for (var prop in obj) {
	        if (hasOwnProperty.call(obj, prop)) result.push(prop);
	      }
	 
	      if (hasDontEnumBug) {
	        for (var i=0; i < dontEnumsLength; i++) {
	          if (hasOwnProperty.call(obj, dontEnums[i])) result.push(dontEnums[i]);
	        }
	      }
	      return result;
	    }
	  })()
	};
//###########################################################################################//

var Misc = new Object();

Misc.wrapText = function(elementID, openTag, closeTag)
/* function to wrap text inside other tags */
/****thanks to richleland from StackOverflow****/
{
    var textArea = $('#' + elementID);
    var len = textArea.val().length;
    var start = textArea[0].selectionStart;
    var end = textArea[0].selectionEnd;
    //if start and end are the same number I take the end of the string
    if (start == end)
    {
    	start = textArea.val().length;
    	end = textArea.val().length;
    }
    var selectedText = textArea.val().substring(start, end);
    var replacement = openTag + selectedText + closeTag;
    textArea.val(textArea.val().substring(0, start) + replacement + textArea.val().substring(end, len));
    
    //then I 
    endrepl = start + replacement.length - closeTag.length;
    textArea.selectRange(endrepl, endrepl);
};




