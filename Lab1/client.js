
//-------------- GLOBAL VARIABLES --------------------------
var welcomeView;
var profileView;
var pwStrength = 4;
var uToken;
var homePage = 'tabs-1';
var foundUser;
//----------------------------------------------------------

//-------------- DISPLAYING PAGES --------------------------

displayView = function(){
console.log(localStorage.getItem("activeToken"));
  if (localStorage.getItem("activeToken") !== null) {
    document.getElementById("content").innerHTML = document.getElementById("profileView").innerHTML;
    uToken = localStorage.getItem("activeToken");
    tryGetData(serverstub.getUserDataByToken(uToken).data.email );
  }
  else {
    document.getElementById("content").innerHTML = document.getElementById("welcomeView").innerHTML;
  }
};

window.onload = function(){
  displayView();
};


//-----------------------------------------------------------

//----------- VALIDATION FOR SIGNUP, LOGIN & LOGOUT ----------------------
function validateSignUp() {
  var pw = document.getElementById("password").value;
  var confirmedpw = document.getElementById("rptpassword").value;
  var fname = document.getElementById("fname").value;
  var lname = document.getElementById("lname").value;
  var gender = document.getElementById("gender").value;
  var email = document.getElementById("email").value;
  var city = document.getElementById("city").value;
  var country = document.getElementById("country").value;
  var feedback = document.getElementById("feedbackArea");
  //may use form in javascript in future

  if (pw !== confirmedpw) {

    feedback.innerHTML = "Passwords not equal";
  }
  else if(pw.length < pwStrength){
    feedback.innerHTML = "Password must be at least " + pwStrength + " characters";
  }
  else if(pw == confirmedpw){
    var ourUser = {"email":email,"password": pw, "firstname":fname, "familyname":lname,"gender":gender,"city":city, "country":country};
    var newUser = serverstub.signUp(ourUser);
    if (newUser.success == true) {
      feedback.innerHTML = newUser.message;
    }
    else {
      feedback.innerHTML = newUser.message;
    }
  }
}

function validateLogin() {
  var loginpw = document.getElementById("loginpw").value;
  var loginu = document.getElementById("uname").value;
  var feedback = document.getElementById("feedbackArea");
  var trylog = serverstub.signIn(loginu,loginpw);

  if (trylog.success == true) {
    uToken = trylog.data;
    feedback.innerHTML = trylog.message;

    localStorage.setItem("activeToken", uToken);
    displayView(profileView);
    changeTab(homePage);
  }
  else {
    displayView(welcomeView);
    feedback.innerHTML = trylog.message;
  }
}

function validateLogout() {
  var tryLogOut = serverstub.signOut(localStorage.getItem("activeToken"));
  var feedback = document.getElementById("feedbackArea");

  if (tryLogOut.success == true) {
    localStorage.removeItem("activeToken");
    uToken = null;
    displayView(welcomeView);
  }
  else {
      feedback.innerHTML = tryLogOut.message;
  }
}

//----------------------------------------------------------------

function tryGetData(userEmail) {
  var tryData = serverstub.getUserDataByEmail(localStorage.getItem("activeToken"), userEmail);
  console.log(tryData);
  var dataContent = document.getElementById("userInfo");
  var wallText = document.getElementById("wallOfContent");
  if (tryData.success == true) {
      dataContent.innerHTML = "Email: " + tryData.data.email + "</br>";
      dataContent.innerHTML += "Name: " + tryData.data.firstname;
      dataContent.innerHTML += " "  + tryData.data.familyname + "</br>";
      dataContent.innerHTML += "Gender: " + tryData.data.gender + "</br>";
      dataContent.innerHTML += "City: " + tryData.data.city + "</br>";
      dataContent.innerHTML += "Country: " + tryData.data.country + "</br>";
  }
  else {
      dataContent.innerHTML  = tryData.message;
  }

  refreshPosts(userEmail);
}

function refreshPosts(userEmail){
  var wallText = document.getElementById("wallOfContent");
  wallText.innerHTML = "";
  if(foundUser == null){
    userEmail = serverstub.getUserDataByToken(uToken).data.email; //If we just wanna refresh current users posts
  }
  else {

    userEmail = foundUser;
  }
  var tryPosts = serverstub.getUserMessagesByEmail(localStorage.getItem("activeToken"), userEmail);
  if (tryPosts.success == true) {
      var arrayOfPosts = tryPosts.data;
      if(arrayOfPosts.length > 0) {
      for (var i = 0; i < arrayOfPosts.length; i++) {
          wallText.innerHTML += "<div class = 'wallchild'>" + arrayOfPosts[i].writer + ": " + arrayOfPosts[i].content + "</div>";

        }
      }
  }
}

function changeTab(object, userEmail){
  var wallText = document.getElementById("wallOfContent");
  var feedback = document.getElementById("feedbackArea");
  document.getElementById("feedbackArea").innerHTML = "";
  document.getElementById('tabs-1').style.display = 'none';
  document.getElementById('tabs-2').style.display = 'none';
  document.getElementById('tabs-3').style.display = 'none';
  document.getElementById(object).style.display = 'block';
  console.log(userEmail);
  if(object === 'tabs-1') {
    if(userEmail == null){
      tryGetData(serverstub.getUserDataByToken(uToken).data.email);
      console.log(tryGetData(serverstub.getUserDataByToken(uToken).data.email));
      foundUser = null;
    }
    else{
      tryGetData(userEmail);
    }
  }
}

function passwordChange() {
  var feedback = document.getElementById("feedbackArea");
  var oldPW = document.getElementById("currPW").value;
  var newPW = document.getElementById("newPW").value;
  var rptPW = document.getElementById("rptnewPW").value;

  if (newPW != rptPW) {
    feedback.innerHTML = "Passwords didnt match, try again!";
  }
  else if(newPW.length < pwStrength){
    feedback.innerHTML = "Your password is too weak use a length of minimun " + pwStrength + " please";
  }
  else {
    var tryPW = serverstub.changePassword(uToken, oldPW, newPW);
    var test = serverstub.getUserDataByToken(uToken);

    if (tryPW.success == true) {

      feedback.innerHTML = tryPW.message;
    }
    else {

      feedback.innerHTML = tryPW.message;
    }
  }


}

function postWall(){
  var content = document.getElementById("wallText").value;
  var wallText = document.getElementById("wallOfContent");
  var recipient;

  if(foundUser !== null) {
    recipient = foundUser;
  }
  else {
    var tryFetchDataRecipient = serverstub.getUserDataByToken(uToken);
    recipient = tryFetchDataRecipient.data.email;
  }


  var sender = uToken;
  var tryFetchDataSender = serverstub.getUserDataByToken(sender);
  var senderEmail = tryFetchDataSender.data.email;

  if(tryFetchDataSender.success == true) {
    var message = serverstub.postMessage(sender, content, recipient);
    if (message.success == true) {
      var content = document.getElementById("wallText").value = null  ;
    }
    else {
        displayView(welcomeView);
      wallText.innerHTML = message.message;
    }
  }
  else {
    wallText.innerHTML = tryFetchDataRecipient.message;
  }
}

function findUser(){
  var tryEmail = document.getElementById("searchText").value;
  foundUser = tryEmail;
  changeTab(homePage, tryEmail);
}
