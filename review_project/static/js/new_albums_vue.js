var albums_ratings = document.getElementsByClassName('item-user-rating')

Array.prototype.forEach.call(albums_ratings, function(el) {
    var mbid = el.id;
    new Vue({
	el : '#' + mbid,
	delimiters : ['[[', ']]'],
	components : {
	    album_popover,
	},
	mounted : function(){
	    this.$refs.popover.onerror = function(e){
		e.preventDefault();
		this.src = default_album_cover

		axios({
		    method : 'post',
		    url : album_update_cover_url,
		    data : getFormData({
			mbid : mbid.replace('ID', '')
		    })
		}).then(response => {
		    
		}).catch(error => {
		    console.log(error);
		})
		    
		    }
	    this.$refs.popover.src = this.$refs.popover.getAttribute('data_src');
	}
    });
});
