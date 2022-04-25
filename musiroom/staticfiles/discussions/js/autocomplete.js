var autocomplete = {
    delimiters : ['[[', ']]'],
    template : `
	<div>
	<input type="text" placeholder="Sujet..." v-model="query" @input="autoComplete" class="form-control" @keydown.down="onArrowDown" @keydown.up="onArrowUp" @keydown.enter.prevent="onEnter" :disabled=isDisabled>
	<div class="panel-footer" v-if="results.length">
	<ul class="list-group position-absolute" style='z-index : 1000'>
	<a class="list-group-item" :class="{ 'active' : arrowCounter == index }" v-for="(result, index) in results" href='#' @click.prevent='select(result)'>[[ result.name ]]</a>
	</ul>
	</div>
	<span class='w3-tag w3-large w3-round mt-2 float-right' :class="{'bg-secondary' : selected == '', 'bg-success' : selected != ''}">
	[[ displaySelected ]]
    </span>
	</div>
	`,
    props : {
	url : {
	    type : String,
	    default : '',
	},
	model : {
	    type : String,
	    default : '',
	}
    },
    data : function(){
	return {
	    query: '',
	    results: [],
	    selected: '',
	    obj_url : '',
	    arrowCounter : -1,
	}
    },
    methods : {
	select(result){
	    this.selected = result.name;
	    this.obj_url=result.url;
	    this.results = []
	    this.arrowCounter = -1;
	},
	autoComplete(){
	    this.results = [];
	    this.arrowCounter = -1;
	    if(this.query.length > 2){
		axios.get(this.url,{
		    params: {
			query: this.query,
			model : this.model,
		    }
		}).then(response => {
		    this.results = response.data;
		}).catch(error => {
		    console.log(error);
		});
	    }
	},
	handleClickOutside(evt) {
	    if (!this.$el.contains(evt.target)) {
		this.results = [];
		this.arrowCounter = -1;
	    }
	},
	onArrowDown() {
	    if (this.arrowCounter < this.results.length-1) {
		this.arrowCounter++;
            }
	},
	onArrowUp() {
            if (this.arrowCounter > 0) {
		this.arrowCounter--;
            }
	},
	onEnter() {
            this.select(this.results[this.arrowCounter]);
	},
    },
    computed : {
	displaySelected(){
	    if (this.selected != ''){
		return this.selected;
	    }
	    else {
		return 'Aucun sujet selectionné';
	    }
	},
	isDisabled(){
	    return this.model === ''
	},
    },
    watch : {
	obj_url: function(newVal){
	    this.$emit('changeurl', newVal);
	}
    },
    mounted() {
	document.addEventListener('click', this.handleClickOutside);
    }
}
