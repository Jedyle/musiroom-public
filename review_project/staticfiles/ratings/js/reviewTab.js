var reviewtab = {
    delimiters : ['[[', ']]'],
    components : {
	'Trumbowyg' : VueTrumbowyg.default,
    },
    props : {
	'url' : String,
    },
    data: function(){
	return {
	    title : '',
	    content : '',
	    data_title: this.title,
	    data_content: this.content,
	    config : {
		btns: [
		    ['strong', 'em', 'del'],
		    ['link'],
		    ['unorderedList'],
		    ['fullscreen'],
		],
		lang: 'fr',
	    },
	}
    },
    
    template :
    `
	<div class="modal-body flex-fill d-flex flex-column">
        <div class="modal-body flex-fill d-flex flex-column">
	<label class="form-label">
        Titre
        <input v-model="data_title" class="form-control">
	</label>
	<div class="flex-fill d-flex flex-column">
        Critique
	<trumbowyg
    v-model="content"
    class="form-control"
    :config="config"></trumbowyg>  
	</div>
        </div>
        <div class="modal-footer text-right">
	<button class="btn color-sanguine" @click="postReview">
        Publier
    </button>
        </div>
	</div>
	`,
    methods : {
	loadReview: function() {
	    axios({
		method:'get',
		url: this.url,
	    }).then(response => {
		if (response.data.exists){
		    this.title = response.data.title;
		    this.content = response.data.content;
		}
		else {
		    this.title = '';
		    this.content = '';
		}
	    }).catch(error => {
		console.log(error);
	    });
	},
	postReview: function(){
	    axios({
		method:'post',
		url: this.url,
		data: getFormData({
		    title : this.data_title,
		    content : this.data_content,
		}),
		xsrfHeaderName: "X-CSRFToken",
	    }).then(response => {
		this.$emit('successReview', {
		    review_url : response.data.url,
		    reviewed : true,
		});
		this.close();
	    }).catch(error => {
		this.$emit('failReview', {error : error});
		this.close();
	    });
	},
	close : function(){
	    this.$emit('close')
	}
    },
    watch : {
	title : function(newVal){
	    this.data_title = newVal;
	},
	content : function(newVal){
	    this.data_content = newVal;
	},
    },
    mounted : function(){
	var wyg_box = document.getElementsByClassName('trumbowyg-box')
	
	Array.prototype.forEach.call(wyg_box, function(el) {
	    el.classList.add('flex-fill')
	    el.classList.add('d-flex')
	    el.classList.add('flex-column')
	    el.classList.add('custom-editor')
	});
	
	var wyg_editor = document.getElementsByClassName('trumbowyg-editor')
	
	Array.prototype.forEach.call(wyg_editor, function(el) {
	    el.classList.add('flex-fill')
	    el.classList.add('custom-editor')
	});
	this.loadReview();
    }
    
}
