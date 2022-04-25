var toggleUserInterest = {
    delimiters : ['[[', ']]'],
    props : {
	interested : Boolean,
	mbid : String,
	url : String,
	trueText : {
	    type : String,
	    default : 'Je veux l\'écouter'
	},
	falseText : {
	    type : String,
	    default : 'Ajouter à mes envies'
	}
    },
    data : function(){
	return {
	    d_interested : this.interested,
	}
    },
    template : `
    	<a class="btn" :class="toggleClass" href="#" @click.prevent="toggleValue"><slot name='content'><i v-show='d_interested' class="fas fa-headphones"></i> [[text]]</slot></a>
	`,
    methods : {
	toggleValue : function(){
	    axios({
		method:'post',
		url: this.url,
		data: getFormData({
		    mbid : this.mbid,
		}),
		xsrfHeaderName: "X-CSRFToken",
	    }).then(response => {
		this.d_interested = response.data.user_interested;
		this.interested = this.d_interested;
		this.$emit('change', this.d_interested);
	    }).catch(error => {
		console.log(error);
	    });
	}
    },
    computed : {
	toggleClass(){
	    if (this.d_interested){
		return 'color-teal'
	    }
	    else {
		return 'btn-outline-dark'
	    }
	},
	text(){
	    if (this.d_interested){
		return this.trueText;
	    }
	    else{
		return this.falseText;
	    }
	}
    },
    watch : {
	interested : function(newVal){
	    if (newVal !== this.d_interested ){
		/* value sent from parent */
		this.toggleValue();
	    }
	}
    }

}
