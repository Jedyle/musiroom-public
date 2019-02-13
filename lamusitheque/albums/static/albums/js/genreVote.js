
function getFormData(object) {
    const formData = new FormData();
    Object.keys(object).forEach(key => formData.append(key, object[key]));
    return formData;
}

axios.defaults.xsrfHeaderName = "X-CSRFToken";


let genre = {
    delimiters : ['[[', ']]'],
    props: {
	type : String,
	upvotes : Number,
	downvotes : Number,
	name : String,
	slug : String,
	url_votes : String,
	url_report : String,
	mbid : String,
    },
    data: function(){
	return {
	    data_type: this.type,
	    data_upvotes: this.upvotes,
	    data_downvotes: this.downvotes,
	}
    },
    template : `<div class="alert alert-dark">
	<h4 class="alert-heading">[[ name ]]</h4> Score : <span class="count">[[ data_upvotes - data_downvotes ]]</span>
	<br>
	<button class="btn" :class="upClass" @click="postVote('up')"> <i class="fas fa-plus"></i> <small>([[ data_upvotes ]])</small></button>
	<button class="btn" :class="downClass" @click="postVote('down')"> <i class="fas fa-minus"></i> <small>([[ data_downvotes ]])</small></button>
	<button class="btn btn-light" :class="cancelClass" @click="postVote('none')">Annuler</button>	 
	<button class="btn btn-default" @click="postAlert">Signaler</button>
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
    },
    methods : {
	postVote : function(vote){
	    var initial_vote = this.data_type
	    axios({
		method:'post',
		url: this.url_votes,
		data: getFormData({
		    type : vote,
		    mbid : this.mbid,
		    slug : this.slug,
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
	postAlert : function() {
	    var conf = confirm("Les signalements doivent seulement concerner les genres abusivement ajoutés dans une perspective malveillante (par exemple R'n'b pour Metallica). Si vous signalez de manière non justifiée, vous ne pourrez plus voter à l'avenir. Voulez vous vraiment signaler ce genre ?");
	    if (conf == true){
		console.log("true");

		axios({
		    method : 'post',
		    url : this.url_report,
		    data : getFormData({
			mbid : this.mbid,
			slug : this.slug,
		    }),
		    xsrfHeaderName: "X-CSRFToken",
		}).then( response => {
		    alert("Votre signalement a été enregistré");
		}).catch( error => {
		});
		
	    }
	    else {
		console.log("false");
	    }
	}

    }
};
