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
	<div class='col-12 col-md-4 col-xl-2 p-0'>
	    <div class="card bg-light">
		<img class="card-img-top d-none d-md-block" :src="review.album_cover" alt="review.album_title">
	<div class="card-body">
	<div class='row'>
	<div class='col-4 col-md-0 d-block d-md-none'>
	<img class="card-img-top d-block d-md-none" :src="review.album_cover" alt="review.album_title">
	</div>
	<div class='col-8 col-md-12'>
		    <h5 class="card-title"><a :href="review.url_album">[[ review.album_title ]]</a></h5>
	<p class="card-text" v-html="review.artists">
	</div>
	</div>
		    </p>
		</div>
	    </div>
	</div>
	<div class='col-12 col-md-8 col-xl-10 border bg-light'>
	<h3 style='font-weight: bold; word-wrap:break-word;'> [[ review.title ]] </h3>
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
