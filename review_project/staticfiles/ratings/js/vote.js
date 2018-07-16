axios.defaults.xsrfHeaderName = "X-CSRFToken";

let vote = {
    delimiters : ['[[', ']]'],
    props: {
	type : String,
	upvotes : Number,
	downvotes : Number,
	url_votes : String,
	element_id : Number,
	can_vote : {
	    type : Boolean,
	    default : true,
	}
    },
    data: function(){
	return {
	    data_type: this.type,
	    data_upvotes: this.upvotes,
	    data_downvotes: this.downvotes,
	}
    },
    template : `<div class="alert alert-dark">
	<div class='col-md-6 col-sm-12'>
	<div class="progress">
	<div class="progress-bar bg-success" role="progressbar" :style="'width:' + percentage + '%'" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
	</div>
	[[ data_upvotes ]] aiment, [[ data_downvotes ]] n\'aiment pas.

	<br>

    </div>
	<div class="text-right" v-if='can_vote'>
	Votez pour cette critique :
	<button class="btn" :class="upClass" @click="postVote('up')"> <i class="fas fa-plus"></i></button>
	<button class="btn" :class="downClass" @click="postVote('down')"> <i class="fas fa-minus"></i> </button>
	<button class="btn btn-light" :class="cancelClass" @click="postVote('none')">Annuler</button>
	</div>
	</div>
	`,
    computed : {
	upClass: function(){
	    return {
		'btn-success disabled' : (this.data_type === 'up'),
		'btn-light' : (this.data_type === 'down' || this.data_type === 'none'),
	    }
	},
	downClass: function(){
	    return {
		'btn-danger disabled' : this.data_type === 'down',
		'btn-light' : (this.data_type === 'up' || this.data_type === 'none'),
	    }
	},
	cancelClass: function(){
	    return {
		' disabled' : (this.data_type === 'none'),
	    }
	},
	percentage: function(){
	    if (this.data_upvotes + this.data_downvotes > 0){
		var percentage = (this.data_upvotes * 100.0) / (this.data_upvotes + this.data_downvotes);
		return percentage
	    }
	    return 0;
	}
    },
    methods : {
	postVote : function(vote){
	    var initial_vote = this.data_type
	    axios({
		method:'post',
		url: this.url_votes,
		data: getFormData({
		    type : vote,
		    element_id : this.element_id
		}),
		xsrfHeaderName: "X-CSRFToken",
	    }
		 ).then(response => {
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
		 }
		       ).catch(function (error) {
			   console.log(error);
		       });
	},
    }
};
