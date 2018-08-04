let ratingpreview = {
    props : {
	'review' : Object,
	'is_anonymous' : Boolean,
	'is_user' : Boolean,
    },
    components : {
	album_popover,
	popover,
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
    data : function(){
	return {
	    user_rating : this.review.user_rating
	}
    },
    delimiters : ['[[', ']]'],
    template : `
	<div>
	<div class="d-flex">
	<div style='min-width: 120px'>
	<img class="card-img-top" :src="review.album_cover" style='height:100px; width:100px; object-fit:cover;' alt="review.album_title">
	</div>
	<div class='flex-grow-1'>
	<h5><a :href="review.url_album">[[ review.album_title ]]</a> <span style='float:right'><span title="Note moyenne" class="w3-tag rounded avg-rating w3-xlarge" style="float : right;"> [[ displayRating(review.average) ]]</span> <span style="float : right;">&ensp;&ensp;</span>  <span v-if='!is_anonymous' title="Moyenne de mes abonnements" class="w3-tag rounded follow-rating w3-xlarge" style="float : right;"> [[ displayRating(review.followees_avg) ]]</span></span> </h5>
	<p v-html="review.artists"></p>
	<p v-if='!is_anonymous' class='text-right'> Ma note : <album_popover @rate="user_rating = $event;" :rating="displayRating(user_rating)" :mbid="review.mbid"></album_popover></p>
    
	    <div class="bd-highlight mb-3">
	<div v-if='!is_user' class="h5 p-2 bd-highlight"><span class="w3-tag bg-secondary">[[ review.rating ]]</span> &ensp; <a target="_blank" :href="review.url_profile"> [[ review.username ]] </a> <template v-if="review.url_review">(<a :href="review.url_review">lire la critique</a>)</template></div>
	<div v-else class="h5 p-2 bd-highlight"><template v-if="review.url_review"><a :href="review.url_review">Lire ma critique</a></template></div>	
	    </div>
	</div>
    </div>
    <hr>
</div>
	`,
}
