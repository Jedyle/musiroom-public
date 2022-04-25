var addalbum = {
    delimiters : ['[[', ']]'],
    template : `<div class="border">
	<a href="#" class="float-right" v-if="!showSearch" @click.prevent="showSearch = true">Ajouter un album...</a>
	<a href="#" class="float-right" v-if="showSearch" @click.prevent="showSearch = false" v-cloak>Fermer la recherche</a>
	
	<template v-if="showSearch" v-cloak>
	
	<br>
	
	<label for="search">Rechercher un album : </label>
	<input type="text" id="search" class="form-control" v-model="query" @keypress.enter="resetSearch">
	
	<br>
	
	<div class="col-12 scrollable">
	
	<p v-for="item in list">
	<template>		    
	<div class="row">
	<div class='col-sm-2'>
	<div class="card">
	<img class="card-img-top" :src="item.cover" :alt="item.title">
	</div>
	</div>
	<div class='col-sm-10 bg-light'>
	<h3 style='font-weight: bold;'> [[ item.title ]]</h3>
	<div class="d-flex">
	<div>
         [[ displayArtists(item.artists) ]]
    </div>
	<div class="ml-auto">
        <button class="btn btn-success" v-if="!isInList(item)" @click="emitAddEvent(item)">Ajouter</button>
	<button class="btn btn-outline-primary" disabled v-else>Dans la liste</button>
    </div>
 </div>
	<br>
	</div>
	</div>
	</template>
	</p>

	<a href="#" @click.prevent='loadSearch' v-if='see_more'>Voir plus</a>
	
    </div>
	<p>Note : seuls les albums déja consultés par au moins une personne sont visibles dans la recherche rapide. Si un album n\'apparait pas directement, faites une recherche dans la barre de navigation et ajoutez l\'album par la suite.</p>
    
	</template>
	</div>`,
    data : function(){
    	return {
    	    showSearch : false,
    	    query : '',
    	    list : [],
	    page : 1,
	    see_more : false,
	    items_per_page : 5,
    	}
    },
    props : {
	search_url : String,
	album_list : Array,
    },
    methods : {
	resetSearch : function(){
	    this.page = 1;
	    this.see_more = true;
	    this.list = [];
	    this.loadSearch();
	},
	loadSearch : function(){
	    if (this.query.length > 1){
		console.log(this.search_url)
		axios({
		    method : 'get',
		    url : this.search_url,
		    params : {
			query : this.query,
			page : this.page,
			items_per_page : this.items_per_page,
		    }		
		}).then(response => {
		    var new_items = response.data.albums
		    if (new_items.length == 0){
			this.see_more = false;
		    }
		    else{
			this.list = this.list.concat(new_items);
			this.page++;
		    }

		}).catch(error => {
		    console.log(error)
		})
		    }
		},
	displayArtists : function(artists){
	    artist_array = []
	    for (var i = 0; i < artists.length; i++){
		artist_array.push(artists[i].name);
	    }
	    return artist_array.join(', ');
	},
	isInList : function(item){
	    for (var i = 0; i < this.album_list.length; i++){
		if (item.mbid === this.album_list[i].mbid){
		    return true;
		}
	    }
	    return false;
	},
	emitAddEvent : function(item){
	    this.$emit('add', item);
	}
    },
    mounted : function(){
    },
}
