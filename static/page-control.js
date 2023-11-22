$(document).ready(function () {
    let selector = $("#settings-item, #back-item, .item-unsel")
    //hover effects are in /static/home/style.css
    selector.click(function () {
        getNewPage($(this))
    });
});


function getNewPage(elmnt) {
    let filePath = elmnt.children().attr('src')
    if (filePath === "/static/img/gear.svg") {
        window.location.href = "/settings"
    } else if (filePath === "/static/img/back.svg") {
        window.location.href = "/"
    }else if (filePath === "/static/img/slider.svg"){
        $.getScript("/static/home/app.js", function (){
            sortMenuOpen()
        })
    } else {
        console.log("Changing tab...")
        fetch("/data/get_current", {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "icon": filePath, "from": window.location.pathname })
        }).then(() => window.location.reload())
    }
}