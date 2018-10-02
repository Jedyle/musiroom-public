 var followees_ratings = {
     delimiters : ['[[', ']]'],
     props : {
	 'url' : String,
     },
     data : function(){
	 return {
	     users : [],
	     loading : true,
	 }
     },
     components : {
	 album_popover,
     },
     template : `
	 <div v-cloak>
	     <div v-show='!loading'>
		 <template v-if='users.length > 0'>

		     <ul class="list-group">
			 <template v-for='user in users'>
			     
			     <li class='list-group-item' v-if='user.ratings.length == 1'>
				 
				 <div class="d-flex">
				     <div style="min-width:70px">
					 <div :style="{ 'width' : '50px' , 'height' : '50px' , 'background-image': 'url(' + user.avatar  + ')', 'background-size' : 'cover', 'background-position' : 'center'}"></div></div>
					     <div class="flex-grow-1">
						 <a :href="user.profile_url">
						     [[ user.username ]]
						 </a> 
						     a donné la note de 
						     <strong>[[ user.ratings[0].score ]]</strong>
							 à l'album
							 <album_popover style="display:inline" class="mt-0" :mbid="user.ratings[0].mbid">
							     <a slot="preview" :href="user.ratings[0].album_url">
								 [[ user.ratings[0].title ]]
							     </a>
							 </album_popover>
					     </div>
				 </div>				     
			     </li>
								 
								 <template v-else>
								     <li class='list-group-item' v-b-toggle="'rat-' + user.username">
									 
				    					 <div class="d-flex">
									     <div style="min-width:70px">
										 <div :style="{ 'width' : '50px', 'height' : '50px', 'background-image' :  'url(' + user.avatar + ')',  'background-size' : 'cover', 'background-position' : 'center'}"></div></div>
										     <div class="flex-grow-1">
											 <a @click.stop :href="user.profile_url">[[user.username]]</a> a noté [[ display(user.ratings.length) ]] albums.
											     <a href="#" @click.prevent><span class="menu-ico-collapse"><i class="fa fa-chevron-down"></i></span></a>
										     </div>
									 </div>
												 
								     </li>
												 <b-collapse :id="'rat-' + user.username">
												     <li class="list-group-item sub-item" v-for='rating in user.ratings'>
													 <div class="d-flex">
													     <div style="min-width:30px">
													     </div>
														 <div style="min-width:50px">
														     <div :style="{ 'width' : '30px',  'height' : '30px',  'background-image' : 'url(' + user.avatar + ')',  'background-size' : 'cover' , 'background-position' : 'center'}"></div>
														 </div>
															 <div class="flex-grow-1">
															     <a :href="user.profile_url">
																 [[ user.username ]]
															     </a> 
																 a donné la note de <strong>[[ rating.score ]]</strong>	
																     à l'album
																     <album_popover style="display:inline" class="mt-0" :mbid="rating.mbid">
																	 <a slot="preview" :href="rating.album_url">
																	     [[ rating.title ]]
																	 </a>
																     </album_popover>
															 </div>
													 </div>				 
												     </li>
												 </b-collapse>
																	     
																	     
								 </template>
																	     
																	     
																	     
																	     
																	     
			 </template>
																	     
		     </ul>
																	     
		 </template>
																	     <template v-else>
																		 Aucun résultat trouvé
																	     </template>
																		 
	     </div>
																		 <div v-show="loading"><br><br><div class="spinner" style="position:relative"></div>
																		 </div>
	 </div>
     `,
     mounted : function(){
	 this.loading = true;
	 axios.get(this.url 
	 ).then(response => {
	     this.users = response.data.users;
	     this.loading = false;
	 }
	 ).catch(error => {
	     console.log(error)
	     this.loading = false;
	 })
     },
     methods : {
	 display : function(nb){
	     if (nb < 15){
		 return nb
	     }
	     else{
		 return 'plus de ' + nb
	     }
	     
	 }
     }
 }
 
 var followees_reviews = {
     delimiters : ['[[', ']]'],
     props : {
	 'url' : String,
     },
     data : function(){
	 return {
	     users : [],
	     loading : true,
	 }
     },
     methods : {
	 display : function(nb){
	     if (nb < 15){
		 return nb
	     }
	     else{
		 return 'plus de ' + nb
	     }
	     
	 }
     },
     components : {
	 album_popover,
     },
     template : `
	 <div v-cloak>
	     <div v-show='!loading'>
		 <template v-if='users.length > 0'>

		     <ul class="list-group">
			 <template v-for='user in users'>
			     
			     <li class='list-group-item' v-if='user.reviews.length == 1'>
				 
				 <div class="d-flex">
				     <div style="min-width:70px">
					 <div :style="{ 'width' : '50px' , 'height' : '50px' , 'background-image': 'url(' + user.avatar  + ')', 'background-size' : 'cover', 'background-position' : 'center'}"></div></div>
					     <div class="flex-grow-1">
						 <a :href="user.reviews[0].review_url">
						     [[ user.reviews[0].review_title ]]
						 </a> par
						     <a :href="user.profile_url">
							 [[ user.username ]]
						     </a>
							 sur l'album
							 <album_popover style="display:inline" class="mt-0" :mbid="user.reviews[0].mbid">
							     <a slot="preview" :href="user.reviews[0].album_url">
								 [[ user.reviews[0].title ]]
							     </a>
							 </album_popover> ([[user.reviews[0].score]]/10)
					     </div>
				 </div>				     
			     </li>
								 
								 <template v-else>
								     <li class='list-group-item' v-b-toggle="'rev-' + user.username">
									 
				    					 <div class="d-flex">
									     <div style="min-width:70px">
										 <div :style="{ 'width' : '50px' , 'height' : '50px' , 'background-image' :  'url(' + user.avatar + ')',  'background-size' : 'cover', 'background-position' : 'center'}"></div></div>
										     <div class="flex-grow-1">
											 <a @click.stop :href="user.profile_url">[[user.username]]</a> a critiqué [[ display(user.reviews.length) ]] albums.
											     <a href="#" @click.prevent><span class="menu-ico-collapse"><i class="fa fa-chevron-down"></i></span></a>
										     </div>
									 </div>
												 
								     </li>
												 <b-collapse :id="'rev-' + user.username">
												     <li class="list-group-item sub-item" v-for='review in user.reviews'>
													 <div class="d-flex">
													     <div style="min-width:30px">
													     </div>
														 <div style="min-width:50px">
														     <div :style="{ 'width' : '30px',  'height' : '30px',  'background-image' : 'url(' + user.avatar + ')',  'background-size' : 'cover' , 'background-position' : 'center'}"></div>
														 </div>
															 <div class="flex-grow-1">
															     <a :href="review.review_url">
																 [[ review.review_title ]]
															     </a> 
																 à propos de l'album
																 <album_popover style="display:inline" class="mt-0" :mbid="review.mbid">
																     <a slot="preview" :href="review.album_url">
																	 [[ review.title ]]
																     </a>
																 </album_popover> ([[review.score]]/10)
															 </div>
													 </div>				 
												     </li>
												 </b-collapse>
																	 
																	 
								 </template>
																	 
																	 
																	 
																	 
																	 
			 </template>
																	 
		     </ul>
																	 
		 </template>
																	 <template v-else>
																	     Aucun résultat trouvé
																	 </template>
																	     
	     </div>
																	     <div v-show="loading"><br><br><div class="spinner" style="position:relative"></div>
																	     </div>
	 </div>
     `,
     mounted : function(){
	 this.loading = true;
	 axios.get(this.url 
	 ).then(response => {
	     this.users = response.data.users;
	     this.loading = false;
	 }
	 ).catch(error => {
	     console.log(error);
	     this.loading = false;
	 })
     }
 }
