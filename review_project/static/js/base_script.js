	 window.addEventListener('load', function(){
	     var allimages= document.getElementsByTagName('img');
	     for (var i=0; i<allimages.length; i++) {
		 if (allimages[i].getAttribute('data-src')) {
		     allimages[i].onerror = function(e){
			 e.preventDefault();
			 this.src = default_cover_url;
			 var mbid = this.id.replace('ID', '')
			 if (mbid.length === 36){
			     axios({
				 method : 'post',
				 url : update_cover_url,
				 data : getFormData({
				     mbid : mbid
				 })
			     }).then(response => {
			     }).catch(error => {
				 console.log(error);
			     })
			 }
			 
			 
		     }
		     allimages[i].setAttribute('src', allimages[i].getAttribute('data-src'));
		 }
	     }
	     var event = new Event('imgLoaded');
	     window.dispatchEvent(event);
	 }, false)
	 
	 var account_menu = document.getElementById('navbarDropdownColl')
	 account_menu.addEventListener('click', function(event){
	     event.preventDefault();
	     document.getElementById('navbarDropdownCollMenu').classList.toggle('show');
	 });

	 document.getElementById('navbarDropdownColl').addEventListener('blur', function(event){
	     document.getElementById('navbarDropdownCollMenu').classList.toggle('show');  
	 })
