let shown = ""
$(document).ready(function () {
    console.log("Doc Ready")
});

$(document).on("keyup", function (e){
    if (e.key === "Escape"){
        $(".bg-block").css('display', 'none');
        $(".login").css("display","none");
        $(".signup").css('display', 'none');
        $(".edit-service").css("display",'none')
        $("#response-signup").text("")
        $("#response-login").text("")
        $("#new_cred").val("")
    }
    if (e.key === "Enter"){
        $("#create-" + shown).click()
    }
})

function signup() {
    shown = "signup"
    // console.log("Displaying Signup Page")
    // $(".bg-block").show();
    $(".bg-block").css('display', 'flex');
    $(".signup").css('display', 'flex');
    $(".login").css("display","none");
    $(".edit-service").css("display",'none')
}

function login(){
    shown = "login"
    $(".bg-block").css('display', 'flex');
    $(".login").css("display","flex");

    $(".signup").css('display', 'none');
    $(".edit-service").css("display",'none')
}

function edit_service(service){
    shown = "edit_service"
    let cred = "#new_cred"
    let input = $(cred)[0]
    $(".bg-block").css('display', 'flex');
    $(".edit-service").css("display",'flex')
    $(".login").css("display","none");
    $(".signup").css('display', 'none');


    $(cred).data("service", service.toLowerCase())

    $("#edit-service-title").text("Change " + service + " account data")
    if (service === "Steam"){
        input.placeholder = "New Steam ID"
    }else if (service === "Playstation"){
        input.placeholder = "New PSID"
    }else{
        input.placeholder = "New API Key"
    }
}


function submit_signup_form() {
    let email = $("#email-signup").val();
    let password = $("#pswrd-signup").val();
    let username = $("#username").val();
    console.log("Sending Signup Data...")
    $.ajax({
        type: "POST",
        url: "/data/accounts/signup",
        data: JSON.stringify({'email': email, 'password': password, 'username':username}),
        contentType: "application/json",
        success: function (response) {
            console.log("SUCCESS!")
            console.log(response)
            let res = response.toString().replaceAll("&#34;", "'").replaceAll("&#39;", "\"")
            let r = JSON.parse(res)
            if (r["code"] !== 201){
                $('#response-signup').text(r["msg"])
            }else if (r["code"] === 201){
                window.location.reload()
            }
        },
        error: function(xhr) {
            //Do Something to handle error
            console.log("ERROR:")
            console.log(xhr)
        }
    });
}

function submit_login_form(){
    let email = $("#email-login").val();
    let password = $("#pswrd-login").val();
    console.log("Sending Login Data...")

    $.ajax({
        type: "POST",
        url: "/data/accounts/login",
        data: JSON.stringify({'email': email, 'password': password}),
        contentType: "application/json",
        success: function (response) {
            console.log("SUCCESS!")
            console.log(response)
            let res = response.toString().replaceAll("&#34;", "'").replaceAll("&#39;", "\"")
            let r = JSON.parse(res)
            console.log(r['code'])
            if (r["code"] !== 200){
                $('#response-login').text(r["msg"])
            }else if (r["code"] === 200){
                window.location.reload()
            }
        },
        error: function(xhr) {
            //Do Something to handle error
            console.log("ERROR:")
            console.log(xhr)
        }
    });
}

function submit_service_form(){
    let cred = $("#new_cred")
    $.ajax({
        type: "POST",
        url: "/data/accounts/add_service",
        data: JSON.stringify({"type":cred.data("service"),"data":cred.val()}),
        contentType: "application/json",
        success: function (response){
            console.log("SUCCESS!")
            let res = response.toString().replaceAll("&#34;", "'").replaceAll("&#39;", "\"")
            let r = JSON.parse(res)
            if (r["code"] !== 202){ // error
                $('#response-service').text(r["msg"])
            }else if (r["code"] === 202){
                window.location.reload() // success
            }
        },
        error: function (xhr) {
            //Do Something to handle error
            console.log("ERROR:")
            console.log(xhr)
        }
    })
}

function toggle_secret_key(img){
    elmnt = $(img)
    if (elmnt.data("state") === "hidden"){
        elmnt.attr("src", "/static/img/eye.png")
        elmnt.data("state", "visible")
        let service = elmnt.data("service")
        $.ajax({
            type:"GET",
            url: "/data/accounts/get_service_" + service,
            success: function (response){
                console.log(response)
                let res = response.toString().replaceAll("&#34;", "'").replaceAll("&#39;", "\"")
                let r = JSON.parse(res)
                if (r['code'] === 202){
                    elmnt.prev().text(r['msg'])
                    elmnt.prev().css({"line-height":"unset","height":"auto", "font-size":"small"})

                }else{
                    elmnt.prev().text(" ")
                }
            },
            error: function (xhr){
                //Do Something to handle error
                console.log("ERROR:")
                console.log(xhr)
            }
        })
    }else if(elmnt.data("state") === "visible"){
        elmnt.attr("src", "/static/img/eye-closed.png")
        elmnt.data("state", "hidden")
        elmnt.prev().text("**********************")
        elmnt.prev().css({"line-height":"22px","height":"15px","font-size":"20px"})

    }
}