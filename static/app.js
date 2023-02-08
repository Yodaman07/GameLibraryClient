

$(document).ready(function () {
    let selector = $("#settings-item, .item-unsel")

    selector.mouseover(function () {
        $(this).css('background', "rgba(132, 161, 213, 0.64)");
    });

    selector.mouseout(function () {
        $(this).css('background', "#242424");
    });


    selector.mousedown(function () {
        $(this).css('background', "rgba(127, 167, 239, 0.88)");
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
    }
}