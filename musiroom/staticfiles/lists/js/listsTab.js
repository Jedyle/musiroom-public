var liststab = {
    delimiters : ['[[', ']]'],
    props : ['lists_url', 'mbid', 'set_item_url', 'delete_item_url', 'title_header'],
    template :
    `
	<div class="modal-body flex-fill d-flex flex-column">
	<h5 class='text-center mt-0 mb-0'>Listes pour [[ title_header ]]</h5>
	<br>
	<div class="modal-body flex-fill d-flex flex-column" style='overflow-y : scroll'>

	<h3>Ajouter à une liste</h3>
    
	<form v-for='elt in lists'>
	<label> <input type="checkbox" :id="'list' + elt.list_id" v-model="elt.is_in_list"> <strong>[[ elt.title ]]</strong> </label>
	<template v-if="elt.is_in_list"><br>Commentaire : <textarea class="form-control" rows="3" v-model="elt.comment"></textarea></template> <br>
	</form>
	
    </div>
	
	<div class="modal-footer text-right">
	<button class="btn color-sanguine" @click.prevent="postLists">
	Confirmer
    </button>
	</div>
	
    </div>
	`,
    methods : {
	loadLists : function(){
	    axios({
		method:'get',
		url: this.lists_url,
		params: {
		    mbid : this.mbid,
		}
	    }).then(response => {
		this.loaded_lists = JSON.parse(JSON.stringify(response.data.lists))		
	    }).catch(error => {
		console.log(error);
	    });

	},
	postLists : function(){
	    var set_item_requests = []
	    var delete_item_requests = []
	    for (var i = 0 ; i < this.lists.length; i++){
		if (JSON.stringify(this.lists[i]) !== JSON.stringify(this.loaded_lists[i])){
		    if (this.lists[i].is_in_list === true){
			set_item_requests.push(axios({
			    method:'post',
			    url: this.set_item_url,
			    data: getFormData({
				list_id : this.lists[i].list_id,
				mbid : this.mbid,
				comment : this.lists[i].comment,
			    })
			}))
		    }
		    else {
			delete_item_requests.push(axios({
			    method:'post',
			    url: this.delete_item_url,
			    data: getFormData({
				list_id : this.lists[i].list_id,
				mbid : this.mbid,
			    })
			})) 
		    }
		}
	    }
	    axios.all(set_item_requests).then( (results) => { 
		return axios.all(delete_item_requests)
	    }).then( (results) => {
		this.resetComments()
		this.loaded_lists = JSON.parse(JSON.stringify(this.lists))
		alert('Album ajouté !')
	    });
	},
	resetComments : function(){
	    for (var i = 0; i < this.lists.length; i++){
		if (!this.lists[i].is_in_list){
		    this.lists[i].comment = '';
		}
	    }
	},
    },
    data : function(){
	return {
	    loaded_lists : [],
	    lists : [],
	}
    },
    mounted : function(){
	this.loadLists()
    },
    watch : {
	loaded_lists : function(newVal){
	    this.lists = JSON.parse(JSON.stringify(newVal))	    
	},
    }
}
