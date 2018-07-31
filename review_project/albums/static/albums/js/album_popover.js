var album_popover_content = {
    delimiters : ['[[', ']]'],
    components : {
	popover,
	'star-rating' : VueStarRating.default
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
	<div class='row'
	>
	<div slot='content' style="position:relative" class="spinner" v-if="loading"></div>
	<template v-else>
	<div class='col-3' :style="{'background' : 'url(' + album_data.cover + ') 50% 50% no-repeat', 'background-size' : 'cover'}"></div>
	<div class='col-9'>
	<h5 class='text-left'>[[album_data.title]]</h5>
	<p class='text-left' v-html='album_data.artists'></p>
	<star-rating :max-rating='10' :star-size='18' v-model='user_rating'></star-rating>
	</div>
	</template>
	</div>
	`,
    watch : {
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
	'star-rating' : VueStarRating.default
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
	}
    },
    template : `
	<popover titleClass='rating-span-popover' contentClass=''>
	<template slot='title'>
	<slot name='preview'>
	<span class="w3-tag rounded user-rating">[[ this.rating ]]</span>
	</slot>
	</template>
	<template slot='content'>
	<keep-alive>
	<component @rate="$emit('rate', $event);" v-bind:is='album_popover_content' v-bind="{ mbid : mbid }"></component>
	</keep-alive>
	</template>
	</popover>
	`,
}
