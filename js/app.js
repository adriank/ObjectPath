$(document).ready(function(){
	$('#tree-structures').popover({
		html:true,
		placement:"right",
		trigger:"hover",
		delay:{ show: 0, hide: 1000 },
		content:$(".tree-details").html(),
		container: '#tree-structures'
	})

	//$('.tooltip-trigger').tooltip()

	if (innerWidth>750) {}

	$("#OPExample1 .code-example span").mouseenter(function(e){
		$(".path ."+e.target.className).addClass("hover")
	})
	$("#OPExample1 .code-example span").mouseleave(function(e){
		$(".path ."+e.target.className).removeClass("hover")
	})
	$("#OPExample1 span.operator").mouseenter(function(e){
		$(".path span."+e.target.className.split(" ")[1]).addClass("hover")
	})
	$("#OPExample1 span.operator").mouseleave(function(e){
		$(".path span."+e.target.className.split(" ")[1]).removeClass("hover")
	})
	$("#OPExample1 .path span.operator").each(function(n,e){
		$(e).popover({
			html:true,
			placement:"bottom",
			trigger:"hover",
			delay:{show:0, hide: 100 },
			animation:false,
			content:$(".hint."+e.className.split(" ")[1]).html(),
			container: e
		}).on('hidden.bs.popover', function () {
			$(e).removeClass("hover")
		})
	})
})
