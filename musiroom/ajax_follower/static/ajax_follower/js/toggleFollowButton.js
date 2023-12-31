var toggleFollowButton = {
    delimiters : ['[[', ']]'],
    props : {
	followed : Boolean,
	user_to_follow : String,
	url : String,
    },
    data : function(){
	return {
	    d_followed : this.followed,
	}
    },
    template : `
    	<a class="btn btn-success btn-block" href="#" @click.prevent="toggleValue" v-if="d_followed">Suivi</a>
	<a class="btn btn-outline-info btn-block" href="#" @click.prevent="toggleValue" v-else>Suivre</a>
	`,
    methods : {
	toggleValue : function(){
	    axios({
		method:'post',
		url: this.url,
		data: getFormData({
		    follow : !this.d_followed,
		    user_to_follow : this.user_to_follow,
		}),
		xsrfHeaderName: "X-CSRFToken",
	    }).then(response => {
		this.d_followed = !this.d_followed;
	    }).catch(error => {
		console.log(error);
	    });
	}
    }

}
