$(function () {
    $('[data-toggle="tooltip"]').tooltip({html: true})

    function inc(index, old){
	var value = parseInt(old)
	if (isNaN(value)){
	    return 1
	}
	return value + 1;
    }

    function dec(index, old){
	var value = parseInt(old) - 1;
	if (value === 0){
	    return '';
	}
	return value;
    }
    
    $('.like-btn').on('click', function(event){
	event.preventDefault();
	var el = this;	 
	axios({
	    method: "post",
	    url: '/commentaires/api/feedback/',
	    data: {
		comment : el.id.replace('like', ''),
		flag : 'like',
	    }
	}).then(response => {
	    if (response.status === 201){
		$(el).addClass('text-primary').removeClass('text-muted');
		var dislike = $(el).siblings('.dislike-btn');
		if (dislike.hasClass('text-primary')){
		    $(el).siblings('.nbdislikes').find('span').text(dec);
		}
		$(el).siblings('.nblikes').find('span').text(inc);
		dislike.addClass('text-muted').removeClass('text-primary');
	    }
	    else if (response.status === 204){
		$(el).removeClass('text-primary').addClass('text-muted');
		$(el).siblings('.nblikes').find('span').text(dec);
	    }
	}).catch( error => {
	    console.log(error)
	});
    });
  
    $('.dislike-btn').on('click', function(event){
	event.preventDefault();
	var el = this;	 
	axios({
	    method : 'post',
	    url: '/commentaires/api/feedback/',
	    data: {
		comment : el.id.replace('dislike', ''),
		flag : 'dislike',
	    }
	}).then(response => {
	    if (response.status === 201){
		$(el).addClass('text-primary').removeClass('text-muted');
		
		var like = $(el).siblings('.like-btn');
		if (like.hasClass('text-primary')){
		    $(el).siblings('.nblikes').find('span').text(dec)
		}
		$(el).siblings('.nbdislikes').find('span').text(inc);
		like.addClass('text-muted').removeClass('text-primary');
		$(el).siblings('.like-btn').addClass('text-muted').removeClass('text-primary');
	    }
	    else if (response.status === 204){
		$(el).removeClass('text-primary').addClass('text-muted');
		$(el).siblings('.nbdislikes').find('span').text(dec);
	    }
	}).catch(error => {
	    console.log(error);
	});
    });
    
})
