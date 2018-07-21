let reviewpreview = {
    props : {
	'review' : Object,
    },
    delimiters : ['[[', ']]'],
    computed : {
	cleanContent : function(){
	    var html = this.review.content;
	    var div = document.createElement("div");
	    div.innerHTML = html;
	    return div.innerText;
	}
    },
    template : `
	<div>
	<h3 style='font-weight: bold;'> [[ review.title ]] </h3>
	<p> [[ cleanContent ]]... </p>
	<p class="text-right"><a :href="review.url_review">Lire la critique</a></p>
	<div class="d-flex bd-highlight mb-3">
	<div class="h5 p-2 bd-highlight"><span class="w3-tag bg-secondary">[[ review.rating ]]</span> &ensp; <a :href="review.url_profile"> [[ review.username ]] </a></div>
	<div class="ml-auto p-2 bd-highlight"> <i class="fas fa-heart"></i> <span>[[ review.num_up ]]</span> </div>
	</div>
	<hr>
	</div>
	`,
    mounted : function(){
    }
};

let reviewpreviewuser = {
    props : {
	'review' : Object,
    },
    delimiters : ['[[', ']]'],
    computed : {
	cleanContent : function(){
	    var html = this.review.content;
	    var div = document.createElement("div");
	    div.innerHTML = html;
	    return div.innerText;
	}
    },
    template : `
 <div>
    <div class="row">
	<div class='col-3'>
	    <div class="card">
		<img class="card-img-top" :src="review.album_cover" alt="review.album_title">
		<div class="card-body">
		    <h5 class="card-title"><a :href="review.url_album">[[ review.album_title ]]</a></h5>
		    <p class="card-text" v-html="review.artists">
		    </p>
		</div>
	    </div>
	</div>
	<div class='col-9'>
	    <h3 style='font-weight: bold;'> [[ review.title ]] </h3>
	    <p> [[ cleanContent ]]... </p>
	    <p class="text-right"><a target="_blank" :href="review.url_review">Lire la critique</a></p>
	    <div class="d-flex bd-highlight mb-3">
		<div class="h5 p-2 bd-highlight"><span class="w3-tag bg-secondary">[[ review.rating ]]</span> &ensp; <a target="_blank" :href="review.url_profile"> [[ review.username ]] </a></div>
		<div class="ml-auto p-2 bd-highlight"> <i class="fas fa-heart"></i> <span>[[ review.num_up ]]</span> </div>
	    </div>
	</div>
    </div>
    <hr>
</div>
	`,
    mounted : function(){
    }
};


let ratingpreview = {
    props : {
	'review' : Object,
    },
    methods : {
	displayRating : function(rating){
	    var zero = 0.01
	    if (parseFloat(rating) < zero){
		return '-'
	    }
	    else{
		return rating.toString().replace(',', '.')
	    }
	},
	
    },
    delimiters : ['[[', ']]'],
    template : `
	<div>
	<div class="row">
	<div class='col-2'>
	    <div class="card">
	<img class="card-img-top" :src="review.album_cover" alt="review.album_title">
	    </div>
	</div>
	<div class='col-10'>
	<h5><a :href="review.url_album">[[ review.album_title ]]</a> <span title="Note moyenne" class="w3-tag bg-secondary w3-xlarge" style="float : right;"> [[ displayRating(review.average) ]]</span> <span style="float : right;">&ensp;&ensp;</span>  <span title="Moyenne de mes abonnements" class="w3-tag color-teal w3-xlarge" style="float : right;"> [[ displayRating(review.followees_avg) ]]</span> </h5>
	<p v-html="review.artists"></p>
	<p class='text-right'> Ma note : <span title="Ma note" class="w3-tag w3-khaki">[[ displayRating(review.user_rating) ]]</span></p>
    
	    <div class="bd-highlight mb-3">
		<div class="h5 p-2 bd-highlight"><span class="w3-tag bg-secondary">[[ review.rating ]]</span> &ensp; <a target="_blank" :href="review.url_profile"> [[ review.username ]] </a></div>
	    </div>
	</div>
    </div>
    <hr>
</div>
	`,
}

let reviewslist = {
    delimiters : ['[[', ']]'],
    props : {
	'reviewlisturl' : String,
	'sort_methods' : Array,
	'component' : Object,
	    },
    components : {
	'paginate' : VuejsPaginate,
	reviewpreview,
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
    :prev-text="'Précédent'"
    :next-text="'Suivant'"
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
	<component :is="component" v-bind="{ review : review }"></component>
	</template>
	</template>

    
	<paginate class="mx-auto"
    ref="paginate2"
    v-model="current_page"
    :page-count="nb_pages"
    :click-handler="changeAndScroll"
    :prev-text="'Précédent'"
    :next-text="'Suivant'"
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
	    console.log('change', numPage, this.current_page);
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
		    this.last_query = query;
		    this.loading = false;
		}).catch(error => {
		    console.log(error);
		    this.loading = false;
		});
	    }
	    else if (method === this.current_sort_method){
		console.log("change page", page)
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
