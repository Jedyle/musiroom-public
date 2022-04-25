let modal = {
    delimiters : ['[[', ']]'],
    template : `
	<transition name="modal">
        <div class="modal-mask text-left" @click="close" v-show="show">
        <div :class="container_class" @click.stop>
        <slot></slot>
        </div>
        </div>
	</transition>
	`,
    props : {
	show : Boolean,
	container_class : {
	    type : String,
	    default : 'modal-container d-flex flex-column',
	},
    },
    methods: {
	close: function () {
	    this.$emit('close');
	}
    },
    mounted: function () {
	document.addEventListener("keydown", (e) => {
	    if (this.show && e.keyCode == 27) {
		this.close();
	    }
	});
    },
};


