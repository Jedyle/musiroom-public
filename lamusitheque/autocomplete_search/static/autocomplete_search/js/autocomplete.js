var autocomplete_search = {
    delimiters : ['[[', ']]'],
    template : `
	<div>
	<input type="text" name="query" autocomplete="off" placeholder="Rechercher..." v-model="query" @input="autoComplete" class="form-control" @keydown.down="onArrowDown" @keydown.up="onArrowUp" @keydown.enter="onEnter" :disabled=isDisabled>
	<div class="panel-footer" v-if="results.length">
	<ul class="list-group position-absolute w-100" style='z-index : 1000'>
	<a class="list-group-item d-flex p-1" :class="{ 'color-light-gray' : arrowCounter == index }" v-for="(result, index) in results" href='#' @click.prevent='select(result)'>
	<div v-if="result.preview" style='min-width: 40px'>
	<div style='width: 30px; height: 30px; background-size:cover; background-position : center;' :style="{'background-image' : 'url(' + result.preview  + ')'}" ></div>
	</div>
	<div class='flex-grow-1'>
	<p class='text-center m-0'>[[ display(result.name)]]</p>
    </div>
    </a>
	</ul>
	</div>
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
	},
	value : {
	    type : String,
	    default : '',
	},
    },
    data : function(){
	return {
	    query: this.value,
	    results: [],
	    selected: '',
	    obj_url : '',
	    arrowCounter : -1,
	}
    },
    methods : {
	select(result){
	    window.location.href=result.url;
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
	display(name){
	    if (name.length > 50){
		return name.substring(0,50) + '...'
	    }
	    return name
	},
	onArrowDown() {
	    if (this.arrowCounter < this.results.length-1) {
		this.arrowCounter++;
            }
	},
	onArrowUp() {
            if (this.arrowCounter >= 0) {
		this.arrowCounter--;
            }
	},
	onEnter(event) {
	    if (this.arrowCounter != -1){
		event.preventDefault();
		window.location.href=this.results[this.arrowCounter].url;
	    }
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
