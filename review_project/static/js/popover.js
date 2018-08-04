var popover = {
    delimiters : ['[[', ']]'],
    props : {
	titleClass : String,
	contentClass : String,
    },
    
    data: function () {
        return {
	    loadedPopup : false,
            showPopup: false,
            timer: '',
            isInInfo: false,
	    transform : "translate(-50%, 10px)",
	    width : 350,
	    position : 'relative',
        }
    },
    methods: {
        hover: function()
        {
            let vm = this;
            this.timer = setTimeout(function() {
                vm.showPopover();
            }, 600);
        },
        hoverOut: function()
        {
            let vm = this;
            clearTimeout(vm.timer);
            this.timer = setTimeout(function() {
                if(!vm.isInInfo)
                {
                    vm.closePopover();
                }
            }, 200);
        },
        hoverInfo: function()
        {
            this.isInInfo = true;
        },
        hoverOutInfo: function()
        {
            this.isInInfo = false;
            this.hoverOut();
        },
        showPopover: function()
        {
	    this.loadedPopup = true;
            this.showPopup = true;
        },
        closePopover: function()
        {
            this.showPopup = false;
        },
	translatePop : function(){
	    var rect = this.$refs.wrap.getBoundingClientRect()
	    var pop_limit = rect.left + rect.width/2 + this.width/2
	    var pop_limit_left = rect.left + rect.width/2 - this.width/2
	    if (pop_limit > window.innerWidth){
		var offset = window.innerWidth - pop_limit
	    	this.transform = "translate(-50%,10px) translate(" + (offset-10) + "px, 0)"
		this.position='relative';
	    }
	    else if (pop_limit_left < 0){
		var offset = -pop_limit_left
		this.transform = "translate(-50%,10px) translate(" + (offset+10) + "px, 0)";
		this.position='relative';
	    }
	    else {
		this.position='relative';
		this.transform = "translate(-50%, 10px)";
	    }
	}
    },
    template :    `
        <div :style="{'position' : position}" class="popover-wrapper mt-0" ref='wrap'>
        <div :class="titleClass" @mouseover="hover" @mouseout="hoverOut"><slot name='title'></slot></div>
        <div ref='popover' :style="{ 'transform' : transform, 'width': width+'px'}" class='popover-content' :class='contentClass' v-if="loadedPopup" v-show="showPopup" v-on:mouseover="hoverInfo" v-on:mouseout="hoverOutInfo">
	<div class='container-fluid'>
	<slot name="content">
        <h3 class='text-left'>Popover</h3>
        <button class='btn'>Follow</button>
        </div>
	</slot>
	</div>
	</div>
	`,
    mounted : function(){
	this.translatePop();
	var vm = this;
	window.addEventListener('resize', function(){
	    vm.translatePop();
	})
    },
}
