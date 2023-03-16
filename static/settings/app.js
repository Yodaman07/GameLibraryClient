$(document).ready(function () {
    console.log("Doc Ready")
});

function signup() {
    // console.log("Displaying Signup Page")
    // $(".bg-block").show();
    $(".bg-block").css('display', 'flex');
    $(".signup").css('display', 'flex');
    $(".login").css("display","none");
}

function login(){
    $(".bg-block").css('display', 'flex');
    $(".signup").css('display', 'none');
    $(".login").css("display","flex");
}


function submit_signup_form() {
    let email = $("#email").val();
    let password = $("#pswrd").val();
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
                $('#response').text(response["msg"])
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
    let email = $("#email").val();
    let password = $("#pswrd").val();
    console.log("Sending Login Data...")

    $.ajax({
        type: "POST",
        url: "/data/accounts/login",
        data: JSON.stringify({'email': email, 'password': password}),
        contentType: "application/json",
        success: function (response) {
            console.log("SUCCESS!")
            console.log(response)

            if (response["code"] !== 201){
                $('#response').text(response["msg"])
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