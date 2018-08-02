let reviewslist = {
    delimiters : ['[[', ']]'],
    props : {
	'reviewlisturl' : String,
	'sort_methods' : Array,
	'component' : Object,
	    },
    components : {
	'paginate' : VuejsPaginate,
    },
    data : function (){
	return {
	    reviewList : [],
	    current_sort_method : '',
	    nb_pages : 1,
	    current_page : 0,
	    query : "",
	    last_query : "",
	    loading : true,
	    is_anonymous : false,
	    is_user : false,
	}
    },
    template :`	<div>
    	<p>
	Tri :
	<template v-for="(sort, index) in sort_methods">
	<a href="#" :id="sort.id" @click.prevent="loadReviewList(sort.id, current_page)" :class="{ 'mark' : sort.id === current_sort_method  }" > [[ sort.name ]]  </a>
	<template v-if="index != sort_methods.length - 1">
	 - 
	</template>
	</template>
	
        </p>

    	<input type="text" id="search" class="form-control" v-model="query" placeholder="Rechercher..." @keypress.enter="loadSearch()">
	
	<br>
	
	<paginate
    ref="paginate1"
    v-model="current_page"
    :page-count="nb_pages"
    :click-handler="changePage"
    :prev-text="'<'"
    :next-text="'>'"
    :container-class="'pagination'"
    :page-class="'page-item'"
    :prev-class="'page-item'"
    :next-class="'page-item'"
    :page-link-class="'page-link sanguine'"
    :prev-link-class="'page-link sanguine'"
    :next-link-class="'page-link sanguine'"
    :active-class="'active color-sanguine'"
    v-show="nb_pages > 1"
	></paginate>

    
	<div style="position:relative"class="spinner" v-if="loading"></div>
    
	<template v-else>
	<p v-if="nb_pages < 1">Aucun résultat trouvé</p>
	<template v-for="review in reviewList">
	<component :is="component" v-bind="{ review : review, is_anonymous : is_anonymous, is_user : is_user }"></component>
	</template>
	</template>

    
	<paginate class="mx-auto"
    ref="paginate2"
    v-model="current_page"
    :page-count="nb_pages"
    :click-handler="changeAndScroll"
    :prev-text="'<'"
    :next-text="'>'"
    :container-class="'pagination'"
    :page-class="'page-item'"
    :prev-class="'page-item'"
    :next-class="'page-item'"
    :page-link-class="'page-link sanguine'"
    :prev-link-class="'page-link sanguine'"
    :next-link-class="'page-link sanguine'"
    :active-class="'active color-sanguine'"
    v-show="nb_pages > 1 && !loading"
	></paginate>
	
    </div>
	`,
    methods : {
	loadSearch : function(){
	    if (this.query === ""){
		this.$el.querySelector('a').click();
	    }
	    else {
		this.loadReviewList('search', this.current_page, this.query)
	    }
	},
	changePage : function(numPage){
	    this.loadReviewList(this.current_sort_method, numPage);
	},
	changeAndScroll : function(page){
	    this.changePage(page);
	    window.scrollTo(0,0);
	},
	loadReviewList : function(method, page, query=""){
	    if (method !== this.current_sort_method || (query !== "" && query !== this.last_query)){
		this.current_page = 1;
		this.loading = true;
		axios.get(this.reviewlisturl, {
		    params : {
			page : 1,
			methode : method,
			query : query,
		    }
		}).then(response => {
		    this.reviewList = response.data.data;
		    this.nb_pages = parseInt(response.data.nbpages);
		    if(response.data.hasOwnProperty('is_anonymous')){
			this.is_anonymous = response.data.is_anonymous;
		    }
		    if(response.data.hasOwnProperty('is_user')){
			this.is_user = response.data.is_user;
		    }
		    this.last_query = query;
		    this.loading = false;
		}).catch(error => {
		    console.log(error);
		    this.loading = false;
		});
	    }
	    else if (method === this.current_sort_method){
		this.loading = true;
		axios.get(this.reviewlisturl, {
		    params : {
			page : page,
			methode : method,
			query : this.last_query,
		    }
		}).then(response => {
		    this.reviewList = response.data.data;
		    this.nb_pages = parseInt(response.data.nbpages);
		    this.loading = false;
		}).catch(error => {
		    console.log(error);
		    this.loading = false;
		})
		    }
	    this.current_sort_method = method;
	    
	}
    },
    mounted : function(){
	this.$el.querySelector('a').click();
    },
    watch : {	
    }
};
