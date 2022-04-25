let genre = {
    delimiters : ['[[', ']]'],
    props: {
	type : String,
	upvotes : Number,
	downvotes : Number,
	name : String,
    },
    template : `<div>
	<h3>[[ name ]]</h3>	     
        Score : <span class="count">[[ upvotes - downvotes ]]</span>
	Pour : <span class="up"> [[ upvotes ]]</span>
	Contre : <span class="down">[[ downvotes ]]</span>
	
	<button class="btn" :class="getUpClass">+</button>
	<button class="btn" :class="getDownClass">-</button>
	<button class="btn btn-default" :class="getCancelClass">Annuler</button>	 
	</div>
	`,
    computed : {
	getUpClass: function(){
	    switch(this.type){
	    case 'up':
		return 'btn-success disabled';
		break;
	    case 'down':
		return 'btn-default';
		break;
	    case 'none' :
		return 'btn-default';
		break;
	    default:
		return 'btn-default';		    
	    }
	},
	getDownClass: function(){
	    switch(this.type){
	    case 'up':
		return 'btn-default';
		break;
	    case 'down':
		return 'btn-danger disabled';
		break;
	    case 'none' :
		return 'btn-default';
		break;
	    default:
		return 'btn-default';		    
	    }
	},
	getCancelClass: function(){
	    switch(this.type){
	    case 'up':
		return '';
		break;
	    case 'down':
		return '';
		break;
	    case 'none' :
		return 'disabled';
		break;
	    default:
		return 'disabled';		    
	    }
	},	 
    }
};


let vm = new Vue({
    el: '#app',
    delimiters : ['[[', ']]'],
    components : {genre},
});
