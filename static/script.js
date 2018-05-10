$('#sform').submit(function(e){
	$(this).find('button[type=submit]').prop('disabled', 'true');
    $(this).find('button[type=button]').prop('disabled', 'true');
    /*$('#querytext').prop('disabled', 'true');*/
    document.getElementById('querytext').onkeydown = function(e){
        e.preventDefault();
    }
    document.getElementById('querytext').oncut = function(e){
        e.preventDefault();
    }
    document.getElementById('querytext').onpaste = function(e){
        e.preventDefault();
    }
    $('#loading-search').css('display','block');
    $('#results-search').css('display','none');
});

function bclick(tp, rtp, li) {
	$('#' + tp + 'button' + li).css('display','none');
	$('#' + rtp + 'button' + li).css('display','inline');
	if ($('#tsnippet' + li).css('display') == 'none'){
		$('#tsnippet' + li).css('display','block');
		$('#csnippet' + li).css('display','none');
	} else {
		$('#tsnippet' + li).css('display','none');
		$('#csnippet' + li).css('display','block');
	}
}
