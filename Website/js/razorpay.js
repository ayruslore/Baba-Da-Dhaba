function done(){
  function getlength(number){
    return number.toString().length;
  }
  nameUser=document.getElementsByName('name')[0].value;
  phoneUser=Number(document.getElementsByName('phone')[0].value);
  addUser=document.getElementsByName('address')[0].value;
  //addUser=addUser.replace(\\g, '-');
  if(nameUser=="" | addUser=="" | phoneUser=="")
    alert("Fill in the details to proceed.");
  else if(getlength(phoneUser)!=10){
    alert("Invald phone number!");
  }
  else{
    if(nameUser!="" & addUser!=""){
      var userData={
        "name": nameUser,
        "number": phoneUser,
        "address": addUser
      };
      $.ajax({
        type: "GET",
        url: nodejsScript+"/confirm",
        data: {
          'Id': uid,
          "name": nameUser,
          "number": phoneUser,
          "address": addUser
        },
        success: function(data){
          console.log("ID sent!");
          console.log(data);
        },
        error: function(data){
          console.log('Nope!');
        }
      });
      userData=JSON.stringify(userData);
      console.log(userData);
      if(document.getElementById('saveDefault').checked==true){
        $.ajax({
          type: "GET",
          url: redisDb+"/set_user_default/"+uid+"/"+userData,
          success: function(data){
            console.log("Success!");
          },
          error: function(data){
            console.log('Nope!');
          }
        });
      }
      alert("Close the webview to proceed! You'll receive a confirmation message soon.");
      document.getElementsByTagName("BODY")[0].style.display="none";
    }
  }

}

var price, nameUser, phoneUser, addUser;

function amount(){
  $.ajax({
    type: "GET",
    url: redisDb+"/get_location_total/"+uid,
    success: function(data){
      data=JSON.parse(data);
      price=data["total"];
      console.log(price);
      document.getElementById('amt').innerHTML="&#8377;"+price;
    },
    error: function(data){
      console.log('Nope!');
    }
  });
}

function userData(){
  $.ajax({
    type: "GET",
    url: redisDb+"/get_user_default/"+uid,
    success: function(data){
      console.log(data);
      data=JSON.parse(data);
      document.getElementsByName('name')[0].value=data['name'];
      //console.log(data['name']);
      if(data['number']!=undefined)
        document.getElementsByName('phone')[0].value=data['number'];
      if(data['address']!=undefined)
        document.getElementsByName('address')[0].value=data['address'];
    },
    error: function(data){
      console.log('Nope!');
    }
  });
}
/*
function razorpay(){
  var options = {
    "key": "rzp_test_HMAxicoOIZn8Xx",
    "amount": price*100, // 2000 paise = INR 20
    "name": "Baba da Dhaba",
    "description": "Payment for your food order",
    "image": "",
    "handler": function (response){
      console.log(response);
      //save payment id
      $.ajax({
        type: "GET",
        url: redisDb+"/"+uid+"/set_payment_key/"+response.razorpay_payment_id,
        success: function(data){
          console.log('Success!');
        },
        error: function(data){
          console.log('Nope!');
        }
      });
      //alert(response.razorpay_payment_id);
      //save address
      $.ajax({
        type: "GET",
        url: redisDb+"/"+uid+"/set_address/payment/"+lat+","+long,
        success: function(data){
          console.log('Success!');
        },
        error: function(data){
          console.log('Nope!');
        }
      });
      //to NodeJS script
      $.ajax({
        type: "GET",
        url: "https://8dd5fd02.ngrok.io/payments",
        data: {
          'key': response.razorpay_payment_id,
          'Id': uid
        },
        success: function(data){
          console.log(data);
        },
        error: function(data){
          console.log('Nope!');
        }
      });
      alert("Close webview to proceed!");
    },
    "prefill": {
      "name": nameUser,
      "email": emailUser,
      "contact": phoneUser
    },
    "notes": {
      "address": document.getElementsByName('address')[0].value
    },
    "theme": {
      "color": "#77cde3"
    }
  };
  var rzp1 = new Razorpay(options);
  rzp1.open();
}
*/
