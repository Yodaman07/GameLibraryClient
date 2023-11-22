// var selected_sort_method;
$(document).ready(function () {
    let sel_color = $("#btn-collection").data("selection-color")
    document.documentElement.style.setProperty("--selection_theme", sel_color)
})

$(window).click(function(e) {
    let data = $(e.target).data("origin")
    if (data !== "dropdown" && data !== "unset" && data !== "hoversort"){
        sortMenuClose()
    }
});

// $(window).mousemove(function (e) {
//     let data = $(e.target).data("origin")
//     if ((data === "hoversort" || data === "dropdown" || data === "unset" || e.target.className === "sort-directions" )){
//         return;
//     }
//     sortDirection(null, false)
// })

// $("#arrow-up").click((arrow)=>{
//     sort(selected_sort_method, arrow.target, "a")
// })
// $("#arrow-down").click((arrow)=>{
//     sort(selected_sort_method, arrow.target, "d")
// })

// $(".arrow, .arrow-sel").click(function (arrow){
//     let methodObj;
//     $(".sort-selection").each(function(a, obj){
//         if(obj.firstElementChild.innerHTML === selected_sort_method){
//             methodObj = obj
//         }
//     })
//
//     if ($("*").hasClass("arrow-sel") && $(arrow.target).hasClass("arrow")){
//         console.log($(arrow.target))
//         $(".arrow-sel").each(function (i, obj){
//             $(obj).removeClass("arrow-sel").addClass("arrow")
//             $(obj).css("background-color", "")
//         })
//     }else{
//         console.log($("*").hasClass("arrow-sel"))
//         console.log($(arrow.target).hasClass("arrow"))
//         console.log($(arrow.target))
//     }
//
//
//     changeArrowState($(arrow.target), "toggle", methodObj)
// })


// function changeArrowState(arrow, state, method){
//     if(state === "toggle"){
//         switch(arrow.hasClass("arrow")){
//             case true:
//                 // console.log("true")
//                 arrow.removeClass("arrow").addClass("arrow-sel")
//                 changeSortMethodColor(method, "active")
//                 break
//             case false:
//                 // console.log("false")
//                 arrow.removeClass("arrow-sel").addClass("arrow")
//                 changeSortMethodColor(method, "inactive")
//                 break
//         }
//     }
// }

// function changeSortMethodColor(sortElmnt, state){
//     // console.log(sortElmnt, state)
//     let sel_color_hex = $("#btn-collection").data("selection-color")
//     if (state === "active"){
//         $(sortElmnt).css("background-color", sel_color_hex)
//     }else if (state === "inactive"){
//         $(sortElmnt).css("background-color", "")
//     }
// }

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

function sortMenuOpen(){
    let dropdown = ".dropdown-container"
    let sort = $("#sort")

    $(dropdown).css("display","flex") //Visible dropdown

    setTimeout(function (){
        sort.removeClass("item-unsel") //Makes the button selected
        sort.addClass("item-sel")
    }, 2)


    sort.attr("data-origin", "dropdown") //Sets the origin of the button to dropdown, so you can't click out of the dropdown with the button
    $("#sort > img").attr("data-origin", "dropdown") //Does the same thing for the img as above
    sort.prependTo(dropdown) //Formats the button
}


function sortMenuClose(){
    let dropdown = ".dropdown-container"
    let sort = $("#sort")

    $(dropdown).css("display","none")

    setTimeout(function (){
        sort.removeClass("item-sel")
        sort.addClass("item-unsel")
    }, 2)

    sort.attr("data-origin", "unset")
    $("#sort > img").attr("data-origin", "unset")
    sort.prependTo("#btn-collection")
}

//Copied from https://stackoverflow.com/questions/3048838/jquery-css-color-value-returns-rgb
// $.fn.getHexBackgroundColor = function() {
//     var rgb = $(this).css('background-color');
//     rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
//     if (rgb == null){
//         return ""
//     }
//     function hex(x) {return ("0" + parseInt(x).toString(16).toUpperCase()).slice(-2);}
//     return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
// }

function resetSortButtons(selectedMode){
    //Help from google ai on search
    //https://www.google.com/search?q=get+all+elements+with+the+same+data+tag+js&oq=get+all+elements+with+the+same+data+tag+js&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRhAMgYIAhBFGEDSAQg3MjUwajBqMagCALACAA&sourceid=chrome&ie=UTF-8
    var allSections = document.querySelectorAll('[data-section]')
    allSections.forEach((button)=>{
        if ($(button).attr("data-section") !== selectedMode){
            $(button).attr("data-active", 0)
        }
    })
}

function sort(method, elmnt, direction){
    // let sel_color_hex = $("#btn-collection").data("selection-color")
    // let hexbg = $(elmnt).getHexBackgroundColor()
    let data_active = $(elmnt).attr("data-active")
    let active
    data_active === '0' ? active = false : active = true
    let prefix;
    let suffix = "_" + direction;

    resetSortButtons(method)
    if (!active){
        // changeSortMethodColor(elmnt, "active")
        switch(method){
            case "A→Z":
                prefix = "a"
                break
            case "Hr→Min":
                prefix = "t"
                break
            case "%":
                prefix = "p"
                break
        }

        //Ensures the other button isn't pressed
        var parent = elmnt.parentElement
        parent.childNodes.forEach((el)=>{
            if ((el !== elmnt) && $(el).is("button")){
                $(el).attr('data-active',0)
            }
        })

        $(elmnt).attr("data-active", 1)
        //https://stackoverflow.com/questions/13524107/how-to-set-data-attributes-in-html-elements
    }else if (active){
        // changeSortMethodColor(elmnt, "inactive")
        prefix = "d"
        suffix = ""
        $(elmnt).attr("data-active", 0)
    } //Button color toggle


    let m = prefix + suffix
    fetch("/sort/" + m).then(
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

// function sortDirection(index, on){
//     if (on){
//         let sort_dir = $(".sort-direction")
//         let sort_list = ['A→Z','Hr→Min','%']
//         selected_sort_method = sort_list[parseInt(index)-1]
//         switch (parseInt(index)){
//             case 1:
//                 sort_dir.css("align-items", 'flex-start')
//                 break
//             case 2:
//                 sort_dir.css("align-items", 'center')
//                 break
//             case 3:
//                 sort_dir.css("align-items", 'flex-end')
//                 break
//         }
//
//         sort_dir.prependTo($('#dropdown-bar'))
//         sort_dir.css("display", "flex")
//
//     }else{
//         let sort_dir = $(".sort-direction")
//         sort_dir.appendTo($('#dropdown-bar'))
//         sort_dir.css("display", "none")
//     }
// }
