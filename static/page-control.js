$(document).ready(function () {
    let selector = $("#settings-item, #back-item, .item-unsel")

    selector.mouseover(function () {
        $(this).css('background', "rgba(36, 36, 36, 0.49)");
    });

    selector.mouseout(function () {
        $(this).css('background', "#242424");
    });


    selector.mousedown(function () {
        $(this).css('background', "rgba(36, 36, 36, 0.88)");
    });

    selector.mouseup(function () {
        $(this).css('background', "#242424");
        getNewPage($(this))
    });

});


function getNewPage(elmnt) {
    let filePath = elmnt.children().attr('src')
    if (filePath === "/static/img/gear.svg") {
        window.location.href = "/settings"
    } else if (filePath === "/static/img/back.svg") {
        window.location.href = "/"
    } else {
        console.log("Changing tab...")
        var socket = io()
        socket.emit("tab-change", { "icon": filePath, "from": window.location.pathname })
        socket.on('new-tab-data', function (data) {
            if (window.location.pathname === "/") {
                update_game_page(data['game_data'], data['themes'], data['current_theme'])
            }
            console.log(data)
        })
    }
}

function update_game_page(game_list, theme_list, current_theme) {
    let current_TList = theme_list[current_theme]
    console.log("Updating css")

    $('#html').css('background', 'linear-gradient(180deg, ' + current_TList['colors'][0] + ' 0%, ' + current_TList['colors'][1] + ' 100%)');
    $(".game").css('background', current_TList['colors'][2])
    $(".settings-background, .game-selection").css('background', current_TList['colors'][3])
    $(".item-sel").css('background', current_TList['colors'][4])

    $(".game-selection").empty()

    for (const i in theme_list) {
        if (i === current_theme){
            let item = $("<div class=\"item-sel\" style=\"background: #80A9F6\"> </div>").append("<img src=" + theme_list[i]['icon'] + " alt=\"Img\" width=\"32px\" height=\"32px\">")
            $(".game-selection").append(item)
        }else{
            let item = $("<div class=\"item-unsel\"> </div>").append("<img src=" + theme_list[i]['icon'] + " alt=\"Img\" width=\"32px\" height=\"32px\">")
            $(".game-selection").append(item)
        }

    }
}