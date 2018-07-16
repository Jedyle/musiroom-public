var circlethumb = {
    props : {
	url : String,
	size : {
	    type : String,
	    default : "60px"
	}
    },
    template : `
	<div class="mx-auto company-header-avatar" :style="{ 'background-image' : 'url(' + url + ')', 'width' : size, 'height' : size }"></div>
    `
}
