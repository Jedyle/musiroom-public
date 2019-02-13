var search = new Vue({
    el : '#autocomplete',
    delimiters : ['[[', ']]'],
    components : {
	'autocomplete' : autocomplete_search,
    },
    data : {
	model : select_val,
    }
    
})
