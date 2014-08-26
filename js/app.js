$(document).ready(function(){
	$('#tree-structures').popover({
		html:true,
		placement:"right",
		trigger:"hover",
		delay:{ show: 0, hide: 1000 },
		content:$(".tree-details").html(),
		container: '#tree-structures'
	})

	$('.dataSource').popover({
		html:true,
		placement:"top",
		trigger:"hover",
		delay:{ show: 0, hide: 1000 },
		content:$(".dataSource-hint").html(),
		container: '.dataSource'
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
			//console.log(e.className)
			$(".path span."+e.className.split(" ")[1]).removeClass("hover")
			//$(e).removeClass("hover")
		})
	})

	var headers=$("#content h2, #content h3"),
			toc=[],
			listType="ul",
			tocNode=$("#TOC")
			console.log(tocNode)
			tocNode.html("<h3>Contents</h3><"+listType+" class=\"list-unstyled\"/>")

			headers.each(function(n,el){
				//console.log(el)
				//console.log(headers[n+1].localName)
				var indent=""
				if (el.localName==="h3") {
					indent=" style=\"margin-left:20px;\""
				}
				toc.push("<li><a href='#"+el.id+"'"+indent+">"+$(el).html()+"</a>")
				//if (el.next("h2,h3") && el.next("h2,h3").get("localName")=="h3"){
				//	toc.push("<"+listType+">")
				//	h3.each(function(sh){
				//		if(sh.previous("h2")===el)
				//			toc.push("<li><a href='#"+sh.getHTML()+"'>"+sh.getHTML()+"</a></li>")
				//	})
				//	toc.push("</"+listType+">")
				//}
				//toc=[]
			})
			$("#TOC "+listType).append(toc.join("")+"</li>")

})
