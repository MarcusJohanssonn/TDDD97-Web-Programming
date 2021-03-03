
//-------------- GLOBAL VARIABLES --------------------------
var welcomeView;
var profileView;
var pwStrength = 4;
var uToken;
var homePage = 'tabs-1';
var foundUser;
var ownEmail;
var isLocal = false;
//----------------------------------------------------------

//-------------- DISPLAYING PAGES --------------------------

displayView = function(){
console.log(localStorage.getItem("activeToken"));
  if (localStorage.getItem("activeToken") !== null) {
    document.getElementById("content").innerHTML = document.getElementById("profileView").innerHTML;
    uToken = localStorage.getItem("activeToken");

  }
  else {
    document.getElementById("content").innerHTML = document.getElementById("welcomeView").innerHTML;
  }
};

window.onload = function(){
//  localStorage.clear();
  displayView();
};


//-----------------------------------------------------------+

function XMLrequest(type, url, jsonData, cbfunction) {
  var xmlhttp = new XMLHttpRequest();

  xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      cbfunction(JSON.parse(xmlhttp.responseText));
      console.log(JSON.parse(xmlhttp.responseText));
    }else if (this.status == 500 || this.status == 400) {
      document.getElementById("feedbackArea").innerHTML = "<h3>" + "FEL DIN NOOB" + "</h3>";
    }
  }

  if (type == 'POST') {
    xmlhttp.open("POST", 'http://localhost:5000/' + url, true);
    xmlhttp.setRequestHeader("Content-type", "application/json");
    xmlhttp.setRequestHeader("token", uToken);
    xmlhttp.send(JSON.stringify(jsonData));
  }
  else if (type == 'GET') {
      xmlhttp.open("GET", 'http://localhost:5000/' + url, true);
      xmlhttp.setRequestHeader("token", uToken);
      xmlhttp.send();
  }

}


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

    XMLrequest('POST', 'signup', ourUser, function(response) {
      if (response.success) {
        console.log(response.message);
        feedback.innerHTML = response.message;
        //Login user
      }
      else {
        feedback.innerHTML = response.message;
      }
      document.getElementById("form_new_user").reset();

    })
  }
}

function validateLogin() {
  var loginpw = document.getElementById("loginpw").value;
  var loginu = document.getElementById("uname").value;
  var feedback = document.getElementById("feedbackArea");
  var ourUser = {"email": loginu, "password": loginpw};
  XMLrequest('POST', 'signin', ourUser, function(response) {
    if (response.success) {
      feedback.innerHTML = response.message;
      uToken = response.token;
      localStorage.setItem("activeToken", uToken);
      console.log("TOKEN FROM LOGIN" + uToken);
      if(!isLocal) {
        socketConnection();
      }

      displayView(profileView);
      changeTab(homePage);

    }
    else {
      feedback.innerHTML = response.message;
    }

  })
}

function validateLogout() {
  var feedback = document.getElementById("feedbackArea");

  XMLrequest('POST', 'signout', "", function(response) {
    if (response.success) {
      feedback.innerHTML = response.message;
      console.log("****REMOVING TOKEN****")
      uToken = null;
      localStorage.removeItem("activeToken");
      displayView(welcomeView);

    }
    else {
      feedback.innerHTML = response.message;
    }
  })
}

//----------------------------------------------------------------

function tryGetData(email) {
  var dataContent = document.getElementById("userInfo");
  var wallText = document.getElementById("wallOfContent");
  //console.log(localStorage.getItem("activeToken"));

  //Get data through token
  if (foundUser == null) {
    XMLrequest("GET", "user/", "", function(response) {
      //console.log(JSON.stringify(response.data));
      if (response.success) {
        dataContent.innerHTML = "Email: " + response.data.email + "</br>";
        dataContent.innerHTML += "Name: " + response.data.firstname;
        dataContent.innerHTML += " "  + response.data.familyname + "</br>";
        dataContent.innerHTML += "Gender: " + response.data.gender + "</br>";
        dataContent.innerHTML += "City: " + response.data.city + "</br>";
        dataContent.innerHTML += "Country: " + response.data.country + "</br>";
        ownEmail = response.data.email;
        refreshPosts(response.data.email);
      }
      else {
          dataContent.innerHTML  = response.message;
      }
    })
  }
  else {
    //Get data through email
    //console.log("HERE IS EMAIL" + email);
    XMLrequest("GET", "browseuser/?email=" + email, "", function(response) {
    //  console.log(JSON.stringify(response.data));
      if (response.success) {
        dataContent.innerHTML = "Email: " + response.data.email + "</br>";
        dataContent.innerHTML += "Name: " + response.data.firstname;
        dataContent.innerHTML += " "  + response.data.familyname + "</br>";
        dataContent.innerHTML += "Gender: " + response.data.gender + "</br>";
        dataContent.innerHTML += "City: " + response.data.city + "</br>";
        dataContent.innerHTML += "Country: " + response.data.country + "</br>";
        refreshPosts(response.data.email);
      }
      else {
          dataContent.innerHTML  = response.message;
      }
    })
  }


}

function refreshPosts(userEmail){
  var wallText = document.getElementById("wallOfContent");
  wallText.innerHTML = "";
  if (userEmail == null){
    userEmail = foundUser;
  }
  if (foundUser == null) {
    XMLrequest("GET", "messagetoken", "", function(response) {

      if (response.success) {
          arrayOfPosts = (response.messages);

          if(arrayOfPosts.length > 0) {
          for (var i = 0; i < arrayOfPosts.length; i++) {
              wallText.innerHTML += "<div class = 'wallchild'>" + arrayOfPosts[i][1] + ": " + arrayOfPosts[i][0] + "</div>";
            }
          }
      }
      else {
          wallText.innerHTML  = response.message;
      }
    })
  }
  else {
    XMLrequest("GET", "browse/?email=" + userEmail, "", function(response) {
      if (response.success) {
          arrayOfPosts = (response.messages);
          if(arrayOfPosts.length > 0) {
          for (var i = 0; i < arrayOfPosts.length; i++) {
              wallText.innerHTML += "<div class = 'wallchild'>" + arrayOfPosts[i][1] + ": " + arrayOfPosts[i][0] + "</div>";
            }
          }
      }
      else {
          wallText.innerHTML  = response.message;
      }
    })
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
  //console.log(userEmail);
  if(object === 'tabs-1') {
    if(userEmail == null){
      foundUser = null;
      tryGetData();
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
    var tryPW = {"password": oldPW, "newPW": newPW};
    XMLrequest('POST', 'changePW', tryPW, function(response) {
      if (response.success) {
        console.log(response.message);
        feedback.innerHTML = response.message;
      }
      else {
        feedback.innerHTML = response.message;
      }

    })

  }


}

function postWall(){
  var content = document.getElementById("wallText").value;
  var wallText = document.getElementById("wallOfContent");
  console.log(foundUser);
  if (foundUser == null) {
    //post at own wall
      var recipient = ownEmail;
  }
  else {
      var recipient = foundUser;
  }

  var ourMessage = {"reciever": recipient, "message": content};
  XMLrequest('POST', 'sendmessage', ourMessage, function(response) {
    if (response.success) {
      console.log(response.message);
      document.getElementById("wallText").value = null;
    }
    else {
      feedback.innerHTML = response.message;
    }

  })
}

function findUser(){
  var tryEmail = document.getElementById("searchText").value;
  foundUser = tryEmail;
  changeTab(homePage, tryEmail);
}

function socketConnection(){
  var websocket = new WebSocket("ws://localhost:5000/api");
  websocket.onmessage = function(serverMessages){
		var msg = serverMessages.data;
    console.log(msg);
		if(msg == "logout" ){     //if we get a message that a new user has logged in via that email logout the old one
			validateLogout();
      websocket.close();
      isLocal = false;
		}

	};

	 websocket.onopen = function(){
    console.log("Socket open");
		websocket.send(localStorage.getItem("activeToken"));    //Start by sending localStorage token
	};

  isLocal = true;
}
