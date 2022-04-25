 var vm = new Vue({
     delimiters : ['[[', ']]'],
     el : '#app',
     data : {
	 currentView : 'all_reviews',
	 currentViewRating : 'all_ratings',
     },
     components : {
	 followees_ratings,
	 followees_reviews,
	 album_popover,
     },
     computed : {
	 currentProperties : function(){
	     if (this.currentView === 'followees_reviews'){
		 return {
		     url : home_followees_reviews_url,
		 }
	     }
	 },
	 currentPropertiesRating : function(){
	     if (this.currentViewRating === 'followees_ratings'){
		 return {
		     url : home_followees_ratings_url,
		 }
	     }
	 }
     }
 })


 var vm_bis = new Vue({
     delimiters : ['[[', ']]'],
     el : '#app_bis',
     data : {
	 currentViewActivity : 'all',
     },
     components : {
	album_popover,
    }, 
 })
