var album_popover_content = {
    delimiters : ['[[', ']]'],
    components : {
	popover,
	'star-rating' : VueStarRating.default,
	'toggleuserinterest' : toggleUserInterest,
    },
    props : {
	mbid : {
	    type : String,
	},
	album_data_url : {
	    type : String,
	    default : album_data_url,
	},
	
    },
    data : function(){
	return {
	    user_rating : 0,
	    loading : true,
	    album_data : {},
	    unwatch : function(){},
	}
    },
    template : `
	<div>
	<div class='row'>
	<div slot='content' style="position:relative" class="spinner" v-if="loading"></div>
	<template v-else>
	<div class='col-4' :style="{'background' : 'url(' + album_data.cover + ') 50% 50% no-repeat', 'background-size' : 'cover'}"></div>
	<div class='col-8'>
	<h5 class='text-left d-flex'><div class='flex-grow-1'><a :href='album_data.album_url'>[[album_data.title]]</a></div><div> <span class='w3-tag rounded avg-rating text-right'>[[album_data.avg]]</span></div></h5>
	<p class='text-left' v-html='album_data.artists'></p>
	<star-rating :max-rating='10' :star-size='18' v-model='user_rating'></star-rating>
	<div class='float-right'>
	<toggleuserinterest :title='displayInterest' :interested='album_data.user_interested' :mbid='mbid' :url='album_data.toggle_interest_url'> <template slot="content"><i class='fas fa-headphones'></i></template> </toggleuserinterest>
	<button type="button" :class='color' class="btn" :title='displayReview' v-if='user_rating != 0' @click.prevent="$emit('show', 'review')"><i class="far fa-comment-alt"></i></button>
	<button type="button" class="btn btn-outline-dark" title="Ajouter à une liste" @click.prevent="$emit('show', 'lists')"><i class="fas fa-list"></i></button>
	</div>
	</div>
	</div>
	
	</template>
	</div>
	</div>
	`,
    computed : {
	displayReview : function(){
	    if (this.album_data.review_exists){
		return 'Modifier ma critique'
	    }
	    else {
		return 'Critiquer'
	    }
	},
	displayInterest : function(){
	    if (this.album_data.user_interested){
		return 'Je veux l\'écouter'
	    }
	    else {
		return 'Ajouter à mes envies'
	    }
	},
	color : function(){
	    if (this.album_data.review_exists){
		return 'color-teal'
	    }
	    else {
		return 'btn-outline-dark'
	    }
	    
	}
    },
    methods : {
	post_vote : function(newVal, oldVal){
	    axios({
		headers : {
		    'content-type' : 'application/json',
		},
		method : 'post',
		url : this.album_data.rate_url,
		data : JSON.stringify({
		    score : newVal,
		}),
		xsrfHeaderName: "X-CSRFToken",
	    }).then(response => {
		this.album_data.review = true;
		this.album_data.user_rating = newVal;
		this.album_data.user_interested = false;
		this.$emit('loaded', this.album_data);
	    }).catch(error => {
		this.unwatch();
		this.user_rating = oldVal;
		var vm = this;
		this.unwatch = this.$watch('user_rating', function(newVal, oldVal){vm.post_vote(newVal, oldVal)});
		alert('Une erreur est survenue : votre note n\'a pas été prise en compte');
		console.log(error);
	    });
	    this.$emit('rate', newVal);
	},
    },
    mounted : function(){	
	axios.get(this.album_data_url, {
	    params : {
		mbid : this.mbid,
	    }
	}).then(response => {
	    this.album_data = response.data;
	    this.user_rating = response.data.user_rating;
	    var vm = this;
	    this.unwatch = this.$watch('user_rating', function(newVal, oldVal){vm.post_vote(newVal, oldVal)});
	    this.$emit('loaded', this.album_data)
	    this.loading = false;
	}).catch(error => {
	    console.log(error);
	})
	    },

}

var album_popover = {
    delimiters : ['[[', ']]'],
    components : {
	popover,
	album_popover_content,
	reviewmodal,
	modal,
    },
    props : {
	rating : {
	    type : String,
	    default : '-',
	},
	mbid : {
	    type : String,
	},
    },
    data : function(){
	return {
	    loading : true,
	    album_data : {},
	    modal_loaded : false,
	    showModal : false,
	    modalView : 'none',	    
	}
    },
    watch : {
	showModal: function (newVal){
	    if (newVal) {
		document.body.classList.add("modal-open");
	    }
	    else {
		document.body.classList.remove("modal-open");
	    }
	    this.$emit('modal', newVal)
	},
    },
    methods : {
	loadReview: function(){
	    this.modalView = 'reviewtab';
	    this.showModal = true;
	},
	loadLists: function(){
	    this.modalView = 'liststab';
	    this.showModal = true;
	},
	updateReview: function(data){
	    if (!this.album_data.review_exists){
		alert('Votre critique a bien été créée !');
	    }
	    else {
		alert('Votre critique a bien été modifiée.');
	    }
	    this.album_data.review_exists = true;
	},
	closeReview: function(){
	    this.showModal = false;
	    this.modalView = 'none';
	},
	load : function(event){
	    if (event === 'review')
	    {
		this.loadReview()
	    }
	    else {
		this.loadLists()

	    }
	}
    },
    computed : {
	modalHandlers : function(){
	    return {
		'close' : this.closeReview,
		'successReview' : this.updateReview,
		'failReview' : (() => {alert('Une erreur est survenue')})
	    }
	}
    },
    template : `
    <div>
	<popover titleClass='rating-span-popover' contentClass=''>
	<template slot='title'>
	<slot name='preview'>
	<span style='cursor : pointer'  class="w3-tag rounded user-rating">[[ this.rating ]]</span>
	</slot>
	</template>
	<template slot='content'>
	<keep-alive>
	<component @rate="$emit('rate', $event);" @loaded="album_data = $event; modal_loaded = true;" @show="load($event)" v-bind:is='album_popover_content' v-bind="{ mbid : mbid }"></component>
	</keep-alive>
	</template>
	</popover>
	<reviewmodal v-if='modal_loaded' :title='album_data.title' :show="showModal" :view="modalView" :lists_url="album_data.lists_url" :set_item_url="album_data.set_item_url" :delete_item_url="album_data.delete_item_url" :mbid="mbid"  :review_url="album_data.review_url" v-on="modalHandlers" :rated="album_data.user_rating != 0" ></reviewmodal>
	</div>
	`,
}
