var lists = {
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
	    lists : [],
	    search: '',
	}
    },
    template : `
	<div class="container-fluid">

	<br>

	<div v-if='user_is_profile'>
	<a class="btn btn-success" :href="create_url">Nouvelle liste</a>
	<br><br>
	
	</div>

	<div class="search-wrapper">
	<label>Filtrer : </label>
	<input type="text" v-model="search" placeholder="Titre.."/>
	</div>
	
	<br>
    
	<ul>
	<li v-for='list in filteredList' :key='list.list_id'>
	<a :href="list.link"> [[ list.title ]]</a> ([[ list.nb_items ]] albums)
	</li>
	</ul>

    </div>

    `,
    computed: {
	filteredList : function() {
	    return this.lists.filter(list => {
		return list.title.toLowerCase().includes(this.search.toLowerCase())
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
	    this.lists = JSON.parse(JSON.stringify(response.data.lists))
	}).catch(error => {
	    console.log(error)
	});
	
    },
    
    
}
