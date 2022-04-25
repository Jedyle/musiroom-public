 var albums_ratings = document.getElementsByClassName('item-user-rating')

 Array.prototype.forEach.call(albums_ratings, function(el) {
     var rating = el.getAttribute('rating');
     var mbid = el.id;
     new Vue({
	 el : '#' + mbid,
	 delimiters : ['[[', ']]'],
	 data : {
	     user_rating : rating
	 },
	 components : {
	     album_popover,
	 },
	 methods : {
	     displayRating : function(rating){
		 if (rating > 0){
		     return rating
		 }
		 else{
		     return '-'
		 }
	     }
	 }
     });
 });
