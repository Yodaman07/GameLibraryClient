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
        fetch("/data/get_current", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "icon": filePath, "from": window.location.pathname })
        }).then(() => window.location.reload())
    }
}