$(document).ready(function () {
    let selector = $("#settings-item, .item-unsel")

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
    }else{
        console.log("fetching")
        fetch("/data/current_theme", {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({"theme_icon": filePath})
        }).then(()=>window.location.reload())
    }
}