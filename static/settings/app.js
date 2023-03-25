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


    $(cred).data("service", service)

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
            if (response["code"] !== 201){
                $('#response-signup').text(response["msg"])
            }else if (response["code"] === 201){
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
            if (response["code"] !== 200){
                $('#response-login').text(response["msg"])
            }else if (response["code"] === 200){
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
            console.log(response)
        },
        error: function (xhr) {
            //Do Something to handle error
            console.log("ERROR:")
            console.log(xhr)
        }
    })
}