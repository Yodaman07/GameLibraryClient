$(document).ready(function(){
})

function searchGames(input) {
    let query = $(input).val()
    let url = "/search_query"

    if (query !== ""){
        url = "/search_query/" + query
    }

    fetch(url).then(
        function (response){
            if (response.status === 200){
                 return response.text()
            }else{
                throw response
            }
        }).then(function (html){
            $(".content").html(html)
    })
}