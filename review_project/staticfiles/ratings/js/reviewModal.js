let reviewmodal = {
    delimiters : ['[[', ']]'],
    components : {
	modal,
	reviewtab,
	liststab,
	'Trumbowyg' : VueTrumbowyg.default,
    },
    props: {
	show : {
	    type : Boolean
	},
	view : {
	    type : String
	},
	review_url : {
	    type : String
	},
	mbid : {
	    type : String
	},
	lists_url : {
	    type : String
	},
	set_item_url : {
	    type : String
	},
	delete_item_url : {
	    type : String
	},
	rated : {
	    type : Boolean,
	    default : true,
	}
    },
    data : function(){
	return {
	    currentView : this.view, 
	}
	
    },
    template : `
	<modal :show="show">
        <div class="modal-header">
	<ul class="nav nav-tabs">
	<li class="nav-item">
	<a class="nav-link" :class="{ 'active' : (currentView === 'reviewtab') }" href="#" @click.prevent="currentView = 'reviewtab'">Critique</a>
	</li>
	<li class="nav-item">
	<a class="nav-link" :class="{ 'active' : (currentView === 'liststab') }" href="#" @click.prevent="currentView = 'liststab'">Listes</a>
	</li>
	</ul>
	<button type="button" class="close" @click="$emit('close')">
	<span aria-hidden="true">&times;</span>
	</button>
        </div>
	<div id="tabContent" class="flex-fill d-flex flex-column">
	<component :is="currentView" v-bind="params" v-on="eventHandlers" v-if="conditions"></component>
	</div>
	</modal>
	`,
    methods : {
	spread : function(event, data){
	    this.$emit(event, data)
	},
    },
    computed : {
	params : function(){
	    if (this.currentView === 'reviewtab'){
		return {
		    url : this.review_url,
		}
	    }
	    else if (this.currentView === 'liststab'){
		return {
		    lists_url : this.lists_url,
		    set_item_url : this.set_item_url,
		    delete_item_url : this.delete_item_url,
		    mbid : this.mbid,
		}
	    }
	},
	conditions : function(){
	    if (this.currentView === 'reviewtab'){
		return this.rated === true
	    }
	    else if (this.currentView === 'liststab'){
		return true
	    }
	},
	eventHandlers : function(){
	    if (this.currentView === 'reviewtab'){
		return {
		    'save' : ((data) => this.spread('save', data)),
		    'close' : ((data) => this.spread('close', data)),
		    'successReview' : ((data) => this.spread('successReview', data)),
		    'failReview' : ((data) => this.spread('failReview', data)),
		}
	    }
	    else if (this.currentView === 'liststab'){
		return {
		}
	    }
	}
    },
    watch : {
	view : function(newVal){
	    this.currentView = this.view;
	},
    }
};
