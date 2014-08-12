$(document).ready(function(){
	$('#tree-structures').popover({
		html:true,
		placement:"bottom",
		trigger:"hover",
		delay:{ show: 0, hide: 1000 },
		content:$(".tree-details").html(),
		container: '#tree-structures'
	})

	//$('.tooltip-trigger').tooltip()

	if (innerWidth>750) {}

})
