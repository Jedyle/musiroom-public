(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.starRatings = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
module.exports = require('./src/ratings');

},{"./src/ratings":2}],2:[function(require,module,exports){
var rest = require('./rest.js');
var utils = require('./utils');

/*********************
 * Initialise ratings
 *********************/
function init () {
    var ratingActions = document.querySelectorAll(".star-ratings-rate-action"),
        i;

    // Add click events to stars
    for (i = 0; i < ratingActions.length; i += 1) {
        bindRatings(ratingActions[i]);
    }
}


/*********************
 * Bind ratings
 *********************/
function bindRatings(el) {
    el.addEventListener("click", ratingClick);

    el.onmouseenter = function () {
        var maxRating = getMaxRating(this);
        var score = this.getAttribute('data-score');
        var parent = utils.findParent(this, "star-ratings");
        parent.querySelector(".star-ratings-rating-foreground").style.width = 100 / maxRating * score + "%";
    };

    el.onmouseleave = function () {
        var avgRating = getAvgRating(this);
        var maxRating = getMaxRating(this);
	var userRating = getUserRating(this);
        var score = this.getAttribute('data-score');
        var parent = utils.findParent(this, "star-ratings");
        var percentage = 100 / maxRating * userRating + "%";
        parent.querySelector(".star-ratings-rating-foreground").style.width = percentage;
    };
}


/*********************
 * Rating click event
 *********************/
function ratingClick(ev) {
    ev.stopPropagation();
    ev.preventDefault();
    var url = this.getAttribute('href');
    var score = this.getAttribute('data-score');
    rate(url, score, this);
}


/*********************
 * Rate instance
 *********************/
function rate(url, score, sender) {
    rest.post(url, {'score': score}, function (rating) {
        updateRating(rating, sender);
        dispatchRateSuccessEvent(rating, sender);
    }, function (errors) {
        showError(errors, sender);
        dispatchRateFailEvent(error, sender);
    });
}


function _getEvent(name, detail) {
    if (typeof CustomEvent === 'undefined') {
        var evt = document.createEvent('CustomEvent');
        evt.initCustomEvent(name, true, true, detail);
        return evt;
    }
    else {
        return new CustomEvent(name, {
            detail: detail,
            bubbles: true,
            cancelable: true
        });
    }
}


function dispatchRateSuccessEvent(rating, sender) {
    sender.dispatchEvent(_getEvent(
        'rate-success',
        {
            sender: sender,
            rating: rating
        }
    ))
}


function dispatchRateFailEvent(error, sender) {
    sender.dispatchEvent(_getEvent(
        'rate-failed',
        {
            sender: sender,
            error: error
        }
    ))
}


function getMaxRating(el) {
    var parent = utils.findParent(el, "star-ratings");
    if (parent) {
        return parseInt(parent.getAttribute('data-max-rating'));
    }

    return -1;
}


function getAvgRating(el) {
    var parent = utils.findParent(el, "star-ratings");
    if (parent) {
        return parseFloat(parent.getAttribute('data-avg-rating'));
    }

    return -1;
}

    function getUserRating(el){
	var parent = utils.findParent(el, "star-ratings");
	if (parent) {
            return parseFloat(parent.getAttribute('data-user-rating'));
	}
	
	return -1;
    }
    

/*********************
 * Update rating
 *********************/
function updateRating(rating, sender) {
    var parent = utils.findParent(sender, "star-ratings"),
        valueElem;

    if (parent === undefined || parent === null) {
        return;
    }
    
    parent.setAttribute("data-avg-rating", rating.average);
    parent.setAttribute("data-user-rating", rating.user_rating);

    var avgElem = parent.getElementsByClassName("star-ratings-rating-average")[0];
    if(avgElem) {
        valueElem = avgElem.getElementsByClassName('star-ratings-rating-value')[0];
        if (valueElem) {
            valueElem.innerHTML = rating.average.toFixed(2);
        }
    }

    var countElem = parent.getElementsByClassName("star-ratings-rating-count")[0];
    if(countElem) {
        valueElem = countElem.getElementsByClassName('star-ratings-rating-value')[0];
        if (valueElem) {
            valueElem.innerHTML = rating.count;
        }
    }

    var userElem = parent.getElementsByClassName("star-ratings-rating-user")[0];
    if(userElem) {
        valueElem = userElem.getElementsByClassName('star-ratings-rating-value')[0];
        if (valueElem) {
            valueElem.innerHTML = rating.user_rating;
        }
    }

    var maxRating =  parseInt(parent.getAttribute('data-max-rating'));
    var percentage = 100 / maxRating * rating.user_rating
    
    parent.querySelector(".star-ratings-rating-foreground").style.width = percentage + '%';

    var ratedCheckbox = document.getElementById('rated');
    console.log('test');
    if (ratedCheckbox.checked == false){
	ratedCheckbox.click();
    }
    console.log(ratedCheckbox);
    
}


function showError (errors, sender) {
    var parent = utils.findParent(sender, "star-ratings");
    if (parent === undefined || parent === null) {
        return;
    }
    parent.querySelector(".star-ratings-errors").innerHTML = errors.error;
    setTimeout(function () {
        parent.querySelector(".star-ratings-errors").innerHTML = "";
    }, 2500);
}

/*********************
 * Only initialise ratings
 * if there is something to rate
 *********************/
document.addEventListener('DOMContentLoaded', function(event) {
    if (document.querySelector('.star-ratings')) {
        init();
    }
});


module.exports = {
    bindRating: bindRatings
};

},{"./rest.js":3,"./utils":4}],3:[function(require,module,exports){
/*jslint browser:true */
"use strict";


var djangoRemarkRest = {
    getCookie: function (name) {
        // From https://docs.djangoproject.com/en/1.7/ref/contrib/csrf/
        var cookieValue = null, cookies, i, cookie;
        if (document.cookie && document.cookie !== '') {
            cookies = document.cookie.split(';');
            for (i = 0; i < cookies.length; i += 1) {
                cookie = cookies[i].trim(); // Doesn't work in all browsers
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    makeRequest: function (url, method, success, fail) {
        var req = new XMLHttpRequest();
        if (req.overrideMimeType !== undefined) {
            req.overrideMimeType("application/json");
        }
        req.open(method, url, true);
        req.setRequestHeader('Content-Type', 'application/json');
        req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        // When done processing data
        req.onreadystatechange = function () {
            if (req.readyState !== 4) {
                return;
            }

            if (req.status >= 200 && req.status <= 299) {
                if (success) {
                    if (req.responseText) {
                        success(JSON.parse(req.responseText));
                    } else { success(); }
                }
            } else {
                if (fail) {
                    fail(JSON.parse(req.responseText));
                }
            }
        };

        return req;
    },

    get: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'GET', success, fail);
        req.send(JSON.stringify(data));
    },

    post: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'POST', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('XSRF-TOKEN'));
        req.send(JSON.stringify(data));
    },

    put: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'PUT', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('XSRF-TOKEN'));
        req.send(JSON.stringify(data));
    },

    patch: function (url, data, success, fail) {
        var req = this.makeRequest(url, 'PATCH', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('XSRF-TOKEN'));
        req.send(JSON.stringify(data));
    },

    "delete": function (url, data, success, fail) {
        var req = this.makeRequest(url, 'DELETE', success, fail);
        req.setRequestHeader("X-CSRFToken", this.getCookie('XSRF-TOKEN'));
        req.send(JSON.stringify(data));
    }
};


module.exports = djangoRemarkRest;

},{}],4:[function(require,module,exports){
/**************************
 * Check if an element has a class
 **************************/
function hasClass (el, name) {
    return (' ' + el.className + ' ').indexOf(' ' + name + ' ') > -1;
}


/**************************
 * Find parent element
 **************************/
function findParent(el, className) {
    var parentNode = el.parentNode;
    while (hasClass(parentNode, className) === false) {
        if (parentNode.parentNode === undefined) {
            return null;
        }
        parentNode = parentNode.parentNode;
    }
    return parentNode
}


module.exports = {
    hasClass: hasClass,
    findParent: findParent
};

},{}]},{},[1])(1)
});
