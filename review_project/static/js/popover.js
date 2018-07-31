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
	    width : 300,
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
	    var pop_limit = rect.left + this.width/2
	    var pop_limit_left = rect.left - this.width/2
	    if (pop_limit > window.innerWidth){
	    	this.transform = "translate(-50%,10px) translate(-" + (this.width/2) + "px, 0)"
	    }
	    else if (pop_limit_left < 0){
		this.transform = "translate(-50%,10px) translate(" + (this.width/2) + "px, 0)"
	    }
	    else {
		this.transform = "translate(-50%, 10px)"
	    }
	}
    },
    template :    `
        <div class="popover-wrapper" ref='wrap'>
        <a href="#" :class="titleClass" @mouseover="hover" @mouseout="hoverOut"><slot name='title'></slot></a>
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
    watch : {
    },
}
