axios.defaults.xsrfHeaderName = "X-CSRFToken";


let discussion_vote = {
    delimiters : ['[[', ']]'],
    props: {
	type : String,
	upvotes : Number,
	downvotes : Number,
	url_votes : String,
	d_id : String,
    },
    data: function(){
	return {
	    data_type: this.type,
	    data_upvotes: this.upvotes,
	    data_downvotes: this.downvotes,
	}
    },
    template : `<div class="mt-2 p-0">
	<p class='text-center m-0'><i class='vote fas fa-angle-up fa-lg' :class="upClass" @click="toggleVote('up')"></i></p>
	<h5 class='m-0 text-center'>[[ data_upvotes - data_downvotes ]]</h5>
	<p class='text-center m-0'><i class='vote fas fa-angle-down fa-lg' :class="downClass" @click="toggleVote('down')"></i></p> 
	</div>
	`,
    computed : {
	upClass: function(){
	    return {
		'text-success disabled' : (this.data_type === 'up'),
	    }
	},
	downClass: function(){
	    return {
		'text-danger disabled' : this.data_type === 'down',
	    }
	},
	cancelClass: function(){
	    return {
		' disabled' : (this.data_type === 'none'),
	    }
	},	 
    },
    methods : {
	toggleVote : function(vote){
	    if (vote === this.data_type){
		this.postVote('none');
	    }
	    else if (vote === 'up') {
		this.postVote('up');
	    }
	    else if (vote === 'down') {
		this.postVote('down');
	    }
	},
	postVote : function(vote){
	    var initial_vote = this.data_type
	    axios({
		method:'post',
		url: this.url_votes,
		data: getFormData({
		    type : vote,
		    id : this.d_id,
		}),
		xsrfHeaderName: "X-CSRFToken",
	    }).then(response => {
		this.data_type = vote;
		if (initial_vote === 'up'){
		    if (vote === 'down'){
			this.data_upvotes--;
			this.data_downvotes++;
		    }
		    else if (vote === 'none'){
			this.data_upvotes--;
		    }		     
		}
		else if (initial_vote === 'down'){
		    if (vote === 'up'){
			this.data_upvotes++;
			this.data_downvotes--;
		    }
		    else if (vote === 'none'){
			this.data_downvotes--;
		    }
		}
		else if (initial_vote === 'none'){
		    if (vote === 'up'){
			this.data_upvotes++;
		    }
		    else if (vote === 'down'){
			this.data_downvotes++;
		    }
		}
	    }).catch(function (error) {
		console.log(error);
	    });
	},
    }
};
