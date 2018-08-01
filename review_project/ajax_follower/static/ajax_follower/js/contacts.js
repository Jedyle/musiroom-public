var contactPreview = {
    delimiters : ['[[', ']]'],
    props: [
	'user',
	'profile_url',
	'avatar',
	'follows',
	'url_follow',
	'is_self',
    ],
    components : {
	'togglefollow' : toggleFollowButton,
	'circlethumb' : circlethumb,
    },
    template : `
	<div class="col-xs-6 col-sm-6 col-md-4 col-lg-3 mb-md-0 mb-4">
	<div class="row">
	<a class='mx-auto' :href="profile_url"><circlethumb :url="avatar" size="72px"></circlethumb></a>
	</div>
	<div class="row">
	<div class="col-12">
	<h5 class="text-center font-weight-bold dark-grey-text mb-3" style="word-wrap:break-word;">
	<strong><a :href="profile_url">[[ user ]]</a></strong>
	</h5>
	<div class="mx-auto" align="center">
	<togglefollow :user_to_follow="user" :followed="follows" :url='url_follow' v-if="(follows !== null) && (!is_self)"></togglefollow>
	[[ follows ]]
	<button class="btn btn-outline-primary" v-else-if="is_self" disabled>C\'est vous !</button>
	</div>
	</div>
	</div>
	</div>
	`,    
}

var contacts = {
    delimiters : ['[[', ']]'],
    components : {
	'contact' : contactPreview,
    },
    props : {
	url : String,
    },
    data : function(){
	return {
	    contact_list : '',
	    options : [
		{ text: 'Tous les contacts', value : 'tout' },
		{ text: 'Abonnés', value : 'abonnes' },
		{ text: 'Abonnements', value : 'abonnements' },
	    ],
	    selected : 'tout',
	    sort : 'alphabetique',
	    sort_options: [
		{ text: 'Ordre alphabétique', value : 'alphabetique' },
		{ text: 'Dernière connexion', value: 'derniere_connexion'}
	    ],
	    loading : false,
	    url_follow : '',
	}
    },
    template : `
	<div class="container-fluid">

    <br>

    <p>
    Filtrer : 
	<select class="select-style" v-model="selected">
	<option v-for="option in options" v-bind:value="option.value">
	[[ option.text ]]
    </option>
	</select>
	</p>

    <p>
    Trier par :
    	<select class="select-style" v-model="sort">
	<option v-for="option in sort_options" v-bind:value="option.value">
	[[ option.text ]]
    </option>
	</select>
	</p>
	
	<br>
	<br>
    
	<div class="loader loader-default" :class="{'is-active' : loading}" v-cloak></div>

	<div class="row">
	<contact v-for="user in contact_list" :key="user.username" :user="user.username" :profile_url="user.profile_url" :avatar="user.avatar" :follows="user.follows" :url_follow="url_follow" :is_self="user.is_self"></contact>

    
	</div>
    </div>
	`,
    methods : {
	loadContacts : function(){
	    this.loading = true;
	    axios({
		method:'get',
		url: this.url,
		params : {
		    type : this.selected,
		    tri : this.sort,
		}
	    }).then(response => {
		this.contact_list = JSON.parse(JSON.stringify(response.data.contacts))
		this.url_follow = response.data.url_follow
	    }).catch(error => {
		console.log(error);
	    });
	    this.loading = false;
	}
	
    },
    mounted : function(){
	this.loadContacts();
    },

    watch : {
	selected : function(val){
	    this.loadContacts();
	},
	sort : function(val){
	    this.loadContacts();
	}
    }
    
}
