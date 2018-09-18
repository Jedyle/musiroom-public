var discussions = {
    delimiters : ['[[', ']]'],
    props : {
	url : {
	    type : String,
	},
	username : {
	    type : String,
	},
	user_is_profile: {
	    type : Boolean,
	},
	create_url : {
	    type : String,
	}
    },
    data : function(){
	return {
	    discussions : [],
	    search: '',
	    is_mounted : false,
	}
    },
    template : `
	<div class="container-fluid">

	<br>

	<div v-if='user_is_profile'>
	<a class="btn btn-success" :href="create_url">Nouvelle discussion</a>
	<br><br>
	
	</div>

	<div class="search-wrapper">
	<label>Filtrer : </label>
	<input type="text" v-model="search" placeholder="Titre.."/>
	</div>
	
	<br>

	<p v-if='filteredDisc.length == 0 && is_mounted'> Aucun résultat trouvé.</p>
    
	<ul class='list-group'>
	<li class='list-group-item' v-for='disc in filteredDisc' :key='disc.disc_id'>
	<a :href="disc.link"> [[ disc.title ]]</a> (sur <a :href='disc.content_object_url'>[[ disc.content_object ]]</a>)
	</li>
	</ul>

    </div>

    `,
    computed: {
	filteredDisc : function() {
	    return this.discussions.filter(disc => {
		return disc.title.toLowerCase().includes(this.search.toLowerCase())
	    })
	}
    },
    mounted : function(){
	axios({
	    method : 'get',
	    url : this.url,
	    params : {
		username : this.username
	    }
	}).then(response => {
	    this.discussions = JSON.parse(JSON.stringify(response.data.discussions));
	    this.is_mounted = true;
	}).catch(error => {
	    console.log(error)
	});
	
    },
    
    
}
